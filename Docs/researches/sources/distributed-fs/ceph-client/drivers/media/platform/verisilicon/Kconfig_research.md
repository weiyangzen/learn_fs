# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Kconfig

Purpose: Kconfig menu for Verisilicon/Hantro media platform drivers. It defines the main Hantro VPU driver option and SoC/feature suboptions that select which hardware integration files are built.

Important symbols: `VIDEO_HANTRO` is a tristate for the `hantro-vpu` module and depends on supported SoC architecture families or `COMPILE_TEST`, `V4L_MEM2MEM_DRIVERS`, and `VIDEO_DEV`; it selects media controller, vb2 DMA-contig/vmalloc, V4L2 mem2mem, and codec helper support for H.264, JPEG, and VP9. `VIDEO_HANTRO_HEVC_RFC` enables optional HEVC reference-frame compression. `VIDEO_HANTRO_IMX8M`, `VIDEO_HANTRO_SAMA5D4`, `VIDEO_HANTRO_ROCKCHIP`, `VIDEO_HANTRO_SUNXI`, and `VIDEO_HANTRO_STM32MP25` are bool SoC support toggles depending on `VIDEO_HANTRO` plus their architecture or `COMPILE_TEST`.

Control flow: kernel configuration enables `VIDEO_HANTRO`, which pulls in common Hantro mem2mem codec code. Per-SoC bools default to `y` when the main driver is enabled and their architecture dependency is satisfied, causing the Makefile to include hardware description/integration objects for that platform.

State and persistence: no runtime state; this file controls build-time inclusion and module availability.

Dependencies and integration: integrates the Verisilicon driver directory with V4L2 mem2mem, media controller, videobuf2, codec control helpers, and architecture-specific platform support. Its symbols are consumed by the sibling Makefile.

Risks: default-`y` SoC suboptions can broaden compile coverage and module size whenever `VIDEO_HANTRO` is enabled. Codec capabilities depend on selected helpers staying aligned with source files in the Makefile; for example AV1 Rockchip objects are built under Rockchip support even though the main symbol help text focuses on broader VPU encode/decode support. HEVC RFC changes memory/bandwidth behavior and should be tested separately.

Test signals: `olddefconfig`/`allmodconfig`/`COMPILE_TEST` coverage; module build as built-in and module; per-SoC configs selecting the expected objects; and runtime probe on i.MX8M, SAMA5D4, Rockchip, Sunxi H6, and STM32MP25 platforms.
