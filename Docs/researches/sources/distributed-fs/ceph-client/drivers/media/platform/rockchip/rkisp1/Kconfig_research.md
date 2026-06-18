# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Kconfig

Purpose: Kconfig entry for building the Rockchip ISP1 V4L2 media driver.

Important APIs/types/functions: defines `CONFIG_VIDEO_ROCKCHIP_ISP1` as a tristate option named "Rockchip Image Signal Processing v1 Unit driver". It depends on V4L platform drivers, V4L2 device support, OF, and either Rockchip/i.MX architecture or `COMPILE_TEST`. It selects media controller, V4L2 subdev API, vb2 DMA-contig and vmalloc backends, V4L2 fwnode, generic MIPI D-PHY, and V4L2 ISP helpers.

Control flow: when enabled, the Makefile builds `rockchip-isp1.o`, which registers the platform driver in `rkisp1-dev.c`. The module name documented to users is `rockchip-isp1`.

State and persistence: build-time configuration only.

Dependencies/integration: integrates the driver into the kernel media platform menu and ensures required media/vb2/PHY infrastructure is selected.

Risks: missing selects/dependencies cause build failures or runtime missing symbols; overly broad selects can build unused infrastructure. The dependency includes `ARCH_MXC` because i.MX8MP uses this ISP block through the same driver.

Test signals: allmodconfig/allyesconfig, COMPILE_TEST on non-Rockchip architectures, module build, and boot probing on RK3399/PX30/i.MX8MP DTs.
