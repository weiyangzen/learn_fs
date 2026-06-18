# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Kconfig

Purpose: Declares the `VIDEO_DW100` configuration option for the NXP i.MX DW100 hardware dewarper mem2mem driver.

Important APIs, types, and functions: `VIDEO_DW100` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_MXC || COMPILE_TEST`; it selects `MEDIA_CONTROLLER`, `V4L2_MEM2MEM_DEV`, and `VIDEOBUF2_DMA_CONTIG`.

Control flow: When the symbol is enabled, the child Makefile builds `dw100.o`. The help text describes the hardware as a memory-to-memory geometrical transform engine driven by a programmable dewarping map.

State and persistence behavior: No runtime state; it persists the build-time inclusion mode of the DW100 driver.

Dependencies and integration points: Coordinates with `drivers/media/platform/nxp/dw100/Makefile`, V4L2 mem2mem core, media controller, and DMA-contiguous vb2 memory.

Risks: If request/control dependencies evolve, this Kconfig may need additional selects. `COMPILE_TEST` can build the driver on non-MXC platforms, so code must keep compile-time hardware assumptions isolated.

Test signals: Build `CONFIG_VIDEO_DW100=y` and `m` with `ARCH_MXC` and `COMPILE_TEST`. Verify the resulting module name is `dw100`.
