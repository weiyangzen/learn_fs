# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Kconfig

Purpose: defines the `VIDEO_ROCKCHIP_RGA` configuration option for the Rockchip Raster 2D Graphics Acceleration Unit V4L2 mem2mem driver.

Important content: the option is tristate, depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_ROCKCHIP || COMPILE_TEST`, and selects `VIDEOBUF2_DMA_SG` plus `V4L2_MEM2MEM_DEV`. Help text identifies accelerated operations such as drawing, scaling, rotation, BitBLT, alpha blending, and blur/sharpness, although the driver implementation in this subset focuses on BitBLT-style transform.

Control flow/state: no runtime behavior; controls whether `rockchip-rga.o` is built in or as a module.

Dependencies/integration: sourced by the Rockchip platform Kconfig and paired with `rga/Makefile`.

Risks and test signals: dependency drift can allow builds without required V4L2/VB2 support. Test `allyesconfig`, `allmodconfig`, and `COMPILE_TEST` across non-Rockchip architectures.
