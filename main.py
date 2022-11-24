import random
import time
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 640  # 在这里改 画布的宽 最好和高成比例放大
CANVAS_HEIGHT = 480  # 在这里改 画布的高 最好和宽成比例放大
CANVAS_CENTER_X = CANVAS_WIDTH / 2  # 画布中心的X轴坐标
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2  # 画布中心的Y轴坐标
IMAGE_ENLARGE = 11  # 在这里改 放大比例 画布放大后，心太小？把这个改大点
HEART_COLOR = "#e86184"  # 心的颜色 在这里改

WINDOWS_TITLE = '爱心~'  # 窗口标题 在这里改
HEART_CENTER_TEXT = '爱你'  # 中间文字内容 在这里改
HEART_CENTER_TEXT_COLOR = '#FFD700'  # 中间文字颜色 在这里改


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    """
    “爱心函数生成器”
    :param shrink_ratio: 放大比例
    :param t: 参数
    :return: 坐标
    """
    # 基础函数
    # x = 16 * (sin(t) ** 3)
    x = 14.6 * (sin(t) ** 3)  # 更尖
    # y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    y = -(14.5 * cos(t) - 4 * cos(2 * t) - 2 * cos(3 * t) - 0.5 * cos(4 * t))  # 更圆润

    # 放大
    x *= shrink_ratio
    y *= shrink_ratio

    # 移到画布中央
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    """
    随机内部扩散
    :param x: 原x
    :param y: 原y
    :param beta: 强度
    :return: 新坐标
    """
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy


def shrink(x, y, ratio):
    """
    抖动
    :param x: 原x
    :param y: 原y
    :param ratio: 比例
    :return: 新坐标
    """
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)  # 这个参数...
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def heart_curve(p):
    """
    爱心的跳动函数参数
    :param p: 参数
    :return: 正弦 + 贝塞尔
    """
    # return curve(p, (.4, .5, .2, .6))
    # https://cubic-bezier.com/ 调整参数的网站
    return curve(p, (.69, .75, .2, .95))  # 在这里改 爱心的贝塞尔曲线参数


def heart_halo_curve(p):
    """
    爱心光环的跳动函数参数
    :param p: 参数
    :return: 正弦 + 贝塞尔
    """
    # return curve(p, (.73,.55,.59,.92))
    # https://cubic-bezier.com/ 调整参数的网站
    return curve(p, (.75, .49, .46, .97))  # 在这里改 光环的贝塞尔曲线参数


def curve(p, b):
    """
    自定义曲线函数，调整跳动周期
    :param b: 贝塞尔参数
    :param p: 参数
    :return: 正弦 + 贝塞尔
    """

    # print('p:', p)
    t = sin(p)

    p0 = b[0]
    p1 = b[1]
    p2 = b[2]
    p3 = b[3]

    t1 = (1 - t)
    t2 = t1 * t1
    t3 = t2 * t1

    r = p0 * t3 + 3 * p1 * t * t2 + 3 * p2 * t * t * t1 + p3 * (t ** 3)  # 贝塞尔计算
    # r = 2 * (2 * sin(4 * p)) / (2 * pi)
    # print('r:', r)
    return r


class Heart:
    """
    爱心类
    """

    def __init__(self, generate_frame=20):
        self._points = set()  # 原始爱心坐标集合
        self._edge_diffusion_points = set()  # 边缘扩散效果点坐标集合
        self._center_diffusion_points = set()  # 中心扩散效果点坐标集合
        self.all_points = {}  # 每帧动态点坐标
        self.build(2000)  # 在这里改 初始的点数，太大可能运行缓慢

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # 爱心
        for _ in range(number):
            t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
            x, y = heart_function(t)
            self._points.add((x, y))

        # 爱心内扩散
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # 爱心内再次扩散
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.24)  # 0.24 这个参数改爱心中间的点点数量，越大数量越多
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        # 调整缩放比例
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.47)  # 魔法参数

        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * heart_curve(generate_frame / 10 * pi)  # 圆滑的周期的缩放比例

        halo_radius = int(4 + 6 * (1 + heart_halo_curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(heart_halo_curve(generate_frame / 10 * pi) ** 2))

        all_points = []

        # 光环
        heart_halo_point = set()  # 光环的点坐标集合，去重
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
            x, y = heart_function(t, shrink_ratio=heart_halo_curve(generate_frame / 10 * pi) + 11)  # 魔法参数
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # 处理新的点
                heart_halo_point.add((x, y))

                random_int_range = int(27 + heart_halo_curve(generate_frame / 10 * pi) * 4)
                x += random.randint(-random_int_range, random_int_range)
                y += random.randint(-random_int_range, random_int_range)
                size = random.choice((1, 1, 2))
                all_points.append((x, y, size))

        # 轮廓
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # 内容
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)

    def frame_count(self):
        return self.generate_frame


def draw(main: Tk, render_canvas_dict: dict, render_heart: Heart, render_frame=0):
    """
    绘图函数
    :param main: TK面板
    :param render_canvas_dict: 画布缓存
    :param render_heart: 心类
    :param render_frame: 当前帧数
    :return: None
    """
    frame_index = render_frame % render_heart.frame_count()

    last_frame_index = (frame_index + render_heart.frame_count() - 1) % render_heart.frame_count()
    if last_frame_index in render_canvas_dict:
        render_canvas_dict[last_frame_index].pack_forget()

    if frame_index not in render_canvas_dict:

        canvas = Canvas(
            main,
            bg='black',  # 在这里改 黑色背景
            height=CANVAS_HEIGHT,
            width=CANVAS_WIDTH
        )
        canvas.pack()

        render_heart.render(canvas, render_frame)
        canvas.create_text(
            CANVAS_CENTER_X,
            CANVAS_CENTER_Y,
            text=HEART_CENTER_TEXT,
            fill=HEART_CENTER_TEXT_COLOR,
            font=('楷体', 48, 'bold')  # 在这里改字体
        )

        render_canvas_dict[frame_index] = canvas
    else:
        render_canvas_dict[frame_index].pack()

    main.after(
        30,  # 在这里改 画面切换间隔时间，越小帧数越高，但是可能会越卡
        draw, main, render_canvas_dict, render_heart, render_frame + 1)


if __name__ == '__main__':
    print('正在启动...')
    start_time = time.time()
    root = Tk()  # 一个Tk界面
    root.title(WINDOWS_TITLE)
    canvas_dict = {}
    heart = Heart(40)  # 在这里改 40为总帧数，帧数越大，花样越多，更占内存
    draw(root, canvas_dict, heart)  # 开始画画~
    end_time = time.time()
    print('爱心魔法耗时 {:.2f} 秒完成 ~'.format(end_time - start_time))
    root.mainloop()
