# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Kconfig

Purpose: this Kconfig entry exposes the Amlogic Meson video decoder staging driver as `CONFIG_VIDEO_MESON_VDEC`. The help text scopes it to video decoder hardware found in GXBB/GXL/GXM chips, while the implementation also contains platform data for later G12A/SM1 revisions.

Important symbols: `VIDEO_MESON_VDEC` is a tristate "Amlogic video decoder driver". It depends on `VIDEO_DEV`, `HAS_DMA`, and either `ARCH_MESON` or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `MESON_CANVAS`.

Control flow and integration: enabling this symbol builds the composite `meson-vdec` module/object from the local Makefile. The selected frameworks match the implementation: V4L2 mem2mem queues, contiguous DMA buffers for source/capture/VIFIFO/workspaces, and Meson canvas IDs for legacy hardware framebuffer addressing.

State and persistence behavior: no runtime state is defined in Kconfig. The selected dependencies determine availability of DMA-contiguous vb2 memory ops, m2m scheduling helpers, and canvas allocation APIs used throughout the driver.

Risks: the help text may understate supported revisions relative to the OF match table. Since the driver is staging and uses firmware plus hardware-specific register programming, `COMPILE_TEST` can validate build coverage but not runtime behavior. Missing firmware files remain runtime failures, not Kconfig constraints.

Test signals: build matrix coverage with `ARCH_MESON=y`, `COMPILE_TEST=y`, module and built-in modes. Runtime tests need OF nodes with DOS, ESPARSER, clocks, resets, AO sysctrl, canvas provider, and IRQ resources.
