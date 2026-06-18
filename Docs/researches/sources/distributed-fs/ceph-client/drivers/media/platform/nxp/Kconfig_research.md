# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Kconfig

Purpose: Top-level Kconfig menu for NXP media platform drivers. It declares camera receiver/bridge drivers and mem2mem engines, and sources subdirectory Kconfig files for i.MX8 ISI, DW100, and i.MX JPEG.

Important APIs, types, and functions: Defines `VIDEO_IMX7_CSI`, `VIDEO_IMX8MQ_MIPI_CSI2`, `VIDEO_IMX_MIPI_CSIS`, `VIDEO_IMX_PXP`, and `VIDEO_MX2_EMMAPRP`, then sources `drivers/media/platform/nxp/dw100/Kconfig` and `drivers/media/platform/nxp/imx-jpeg/Kconfig`. Each option expresses architecture, V4L2, DMA, media-controller, fwnode, subdev, mem2mem, and videobuf2 dependencies.

Control flow: Build configuration enters this file under the media platform tree. Enabled symbols select helper frameworks so corresponding objects in the Makefile can be compiled and linked. Subdirectory source lines extend the menu for nested drivers.

State and persistence behavior: No runtime state. Persistent effect is the generated kernel configuration symbols that decide which drivers exist in the built kernel or modules.

Dependencies and integration points: Integrates with `drivers/media/platform/nxp/Makefile`; each `config` symbol maps to an object or subdirectory. It also coordinates with architecture symbols (`ARCH_MXC`, `SOC_IMX27`) and `COMPILE_TEST`.

Risks: Missing `select` lines can cause link failures or disabled runtime APIs. Overly broad `COMPILE_TEST` coverage may expose code to architectures without real hardware assumptions. Help text and symbol names are user-facing kernel configuration ABI.

Test signals: `allyesconfig`, `allmodconfig`, and targeted configs should verify symbol dependency closure. `scripts/kconfig/conf` and build tests should cover both built-in and module modes, especially subdirectory Kconfig source paths.
