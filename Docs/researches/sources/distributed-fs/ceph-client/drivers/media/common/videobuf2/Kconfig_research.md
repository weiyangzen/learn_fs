# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/Kconfig

Purpose: Declares the internal Kconfig symbols that control compilation of the Videobuf2 core and memory backends. These symbols are selected by media drivers and higher-level V4L2/DVB options rather than presented with prompts in this file.

Important APIs, types, and functions: defines tristate symbols `VIDEOBUF2_CORE`, `VIDEOBUF2_V4L2`, `VIDEOBUF2_MEMOPS`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `VIDEOBUF2_DMA_SG`, and `VIDEOBUF2_DVB`. `VIDEOBUF2_CORE` selects `DMA_SHARED_BUFFER`; contiguous and vmalloc backends select core, memops, and DMA shared-buffer support; scatter-gather selects core and memops; DVB selects core.

Control flow: Kconfig resolution determines which videobuf2 objects the Makefile will build. Drivers select the backend they need, which in turn selects common support. There is no executable control flow; the file participates in build-time dependency propagation.

State and persistence behavior: state is limited to kernel configuration. Selected symbols persist in the generated `.config` and drive which modules or built-in objects exist. No runtime state, storage, or data structures are defined here.

Dependencies and integration points: consumed by `drivers/media/common/videobuf2/Makefile` through `obj-$(CONFIG_...)` rules. Integrates with media driver Kconfig entries that select vb2 queue support and with DMA-buf infrastructure through `DMA_SHARED_BUFFER`.

Risks and invariants: missing `select` dependencies can create link failures when a backend is enabled without its common helpers. Over-broad selects can pull DMA-buf support into configurations unexpectedly. Because symbols are promptless, discoverability depends on selecting drivers and on Kconfig dependency hygiene elsewhere.

Test signals: build media configurations with each backend as built-in and module. Run `oldconfig`/`allyesconfig` style coverage to detect dependency loops and ensure `VIDEOBUF2_CORE` is enabled whenever a backend needs `videobuf2-common.o`. Link tests should include V4L2-only, DVB-only, DMA-contig, DMA-SG, and vmalloc users.
