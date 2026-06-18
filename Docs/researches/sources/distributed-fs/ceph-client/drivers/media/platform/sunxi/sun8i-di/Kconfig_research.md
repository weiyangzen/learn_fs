# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Kconfig

Purpose: defines the build option for the Allwinner deinterlace V4L2 mem2mem driver.

Important APIs and symbols: `VIDEO_SUN8I_DEINTERLACE` is a tristate depending on V4L mem2mem drivers, video, sunxi or compile-test, common clock, reset, OF, and PM. It selects videobuf2 DMA-contig and `V4L2_MEM2MEM_DEV`.

Control flow: when enabled, the Makefile builds `sun8i-di.o`.

State and persistence: build configuration only.

Dependencies and integration points: exposes a deinterlace/scaling unit as a V4L2 memory-to-memory video device.

Risks: no media-controller dependency because it is an isolated mem2mem engine. Runtime requires clocks, reset, IRQ, and coherent DMA.

Test signals: module build and V4L2 mem2mem device registration on compatible hardware.
