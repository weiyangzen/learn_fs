# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Kconfig

Purpose: Declares the `VIDEO_IMX8_JPEG` Kconfig option for the i.MX8 QXP/QM integrated JPEG encoder/decoder V4L2 mem2mem driver.

Important APIs, types, and functions: `VIDEO_IMX8_JPEG` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `ARCH_MXC || COMPILE_TEST`, and `VIDEO_DEV`; it selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `V4L2_JPEG_HELPER`.

Control flow: Enabling the symbol causes the Makefile to build the combined `mxc-jpeg-encdec` object from hardware and core source files.

State and persistence behavior: No runtime state; build-time selection controls module availability.

Dependencies and integration points: Coordinates with `imx-jpeg/Makefile`, the V4L2 JPEG parser/helper library, mem2mem core, and DMA-contiguous vb2 memory.

Risks: The driver relies on `V4L2_JPEG_HELPER`; missing select would create unresolved symbols. Architecture/compile-test settings need to keep non-MXC build coverage possible.

Test signals: Build tests for `CONFIG_VIDEO_IMX8_JPEG=y/m`, plus compile-test builds on non-MXC architectures.
