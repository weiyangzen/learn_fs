# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Kconfig

Purpose: declares Xilinx media platform driver configuration symbols. `VIDEO_XILINX` is the base composite video IP pipeline driver and selects media-controller, V4L2 subdev API, contiguous DMA vb2 memory, and V4L2 fwnode support.

Important entries: `VIDEO_XILINX` depends on platform V4L drivers, `VIDEO_DEV`, OF, and DMA; `VIDEO_XILINX_CSI2RXSS` depends on the base driver; `VIDEO_XILINX_TPG` depends on the base and selects `VIDEO_XILINX_VTC`; `VIDEO_XILINX_VTC` depends on the base. The help texts identify the composite pipeline, MIPI CSI-2 Rx subsystem, test pattern generator, and video timing controller.

Control flow/state: no runtime logic; Kconfig controls which objects are compiled and which helper symbols are pulled into a kernel build. Dependencies integrate with the media subsystem and device-tree platforms.

Risks: missing `VIDEO_XILINX` prevents the CSI-2/TPG/VTC drivers from being available; missing selected media/vb2 dependencies breaks runtime registration or DMA queue support. Test signals are Kconfig dependency resolution for built-in/module builds and compile coverage for all enabled combinations.
