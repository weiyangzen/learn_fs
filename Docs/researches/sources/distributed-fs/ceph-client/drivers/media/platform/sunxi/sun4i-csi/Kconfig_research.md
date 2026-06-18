# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Kconfig

Purpose: defines the build option for the Allwinner A10 camera sensor interface V4L2 driver.

Important APIs and symbols: `VIDEO_SUN4I_CSI` is a tristate option. It depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, `COMMON_CLK`, `RESET_CONTROLLER`, `HAS_DMA`, and `ARCH_SUNXI || COMPILE_TEST`. It selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_FWNODE`.

Control flow: when selected, the directory Makefile links the `sun4i-csi.o` module from core, DMA, and V4L2 implementation files. The help text identifies the module name as `sun4i_csi`.

State and persistence: only affects persistent kernel build configuration. Runtime state is in the driver C files.

Dependencies and integration points: declares the media controller, V4L2 subdevice, fwnode graph, and DMA-contiguous buffer dependencies needed by the sun4i CSI media pipeline.

Risks: missing `HAS_DMA` or clock/reset dependencies would make runtime resource acquisition impossible. The option is narrow to A10-class CSI but also covers compatibles listed in the implementation.

Test signals: Kconfig visibility under sunxi or `COMPILE_TEST`, module build as `sun4i-csi.o`, and successful dependency auto-selection in `allyesconfig`.
