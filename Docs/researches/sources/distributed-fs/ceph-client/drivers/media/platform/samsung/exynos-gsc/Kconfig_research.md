# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Kconfig

Purpose: declares the kernel configuration option for the Samsung Exynos5 G-Scaler V4L2 driver.

Important APIs and symbols: `VIDEO_SAMSUNG_EXYNOS_GSC` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_EXYNOS || COMPILE_TEST`; it selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow: when enabled, the local Makefile builds `exynos-gsc.o` from core, mem2mem, and register implementation objects.

State and persistence: no runtime state; the selected tristate persists in the kernel configuration and controls whether the driver is built-in, modular, or absent.

Dependencies and integration points: integrates the G-Scaler driver with V4L2 mem2mem, vb2 DMA-contig, and Exynos platform builds while retaining compile-test coverage on other architectures.

Risks: the option only expresses core build dependencies; runtime still needs device-tree nodes, clocks, IRQ, and memory resources. Missing media-controller or PM combinations are caught by broader media dependencies rather than this file.

Test signals: Kconfig visibility on Exynos and COMPILE_TEST builds, `allmodconfig`, and module build of `exynos-gsc`.
