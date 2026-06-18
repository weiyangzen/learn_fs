# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Makefile

Purpose: links the sun4i CSI driver from its core, DMA, and V4L2 source files.

Important APIs and entries: `sun4i-csi-y` contains `sun4i_csi.o`, `sun4i_dma.o`, and `sun4i_v4l2.o`; `obj-$(CONFIG_VIDEO_SUN4I_CSI)` emits the composite `sun4i-csi.o`.

Control flow: kbuild compiles each component and links them into one module or built-in object according to `VIDEO_SUN4I_CSI`.

State and persistence: no runtime state. It preserves the module boundary between the platform driver, buffer/IRQ engine, and V4L2 ioctl/subdev layer.

Dependencies and integration points: consumes the Kconfig symbol in the same directory and exports no separate modules for the subcomponents.

Risks: adding a source file without this list would silently omit functionality from the module. Renaming any object requires synchronized updates here.

Test signals: `make M=drivers/media/platform/sunxi/sun4i-csi` with `CONFIG_VIDEO_SUN4I_CSI=m` should produce one module containing all three objects.
