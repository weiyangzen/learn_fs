# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Kconfig

Purpose: build configuration for the Samsung S5P/Exynos JPEG codec V4L2 mem2mem driver.

Important declarations: `config VIDEO_SAMSUNG_S5P_JPEG` is a tristate option depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_S5PV210 || ARCH_EXYNOS || COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow and integration: enabling the symbol builds the `s5p-jpeg` aggregate object, which registers encoder and decoder mem2mem video nodes from `jpeg-core.c`.

State and persistence: no runtime state; build metadata only.

Risks: missing selected dependencies would break vb2/mem2mem use. Architecture gating controls driver visibility for non-Samsung builds except compile-test coverage.

Test signals: Kconfig visibility and build as built-in/module across Exynos, S5PV210, and `COMPILE_TEST` configurations.
