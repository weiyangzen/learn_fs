# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Kconfig

## Purpose
This Kconfig file declares the Samsung S5P/Exynos4 camera subsystem menu and build-time feature switches for FIMC, MIPI-CSIS, FIMC-LITE, and FIMC-IS support.

## Important APIs, Types, and Functions
`VIDEO_SAMSUNG_EXYNOS4_IS` is the top-level tristate and selects media-controller, V4L2 subdev API, and V4L2 fwnode support. `VIDEO_EXYNOS4_IS_COMMON` builds shared helpers. `VIDEO_S5P_FIMC` enables the FIMC/CAMIF camera interface and mem2mem postprocessor. `VIDEO_S5P_MIPI_CSIS` enables the MIPI-CSI2 receiver. `VIDEO_EXYNOS_FIMC_LITE` enables FIMC-LITE. `VIDEO_EXYNOS4_FIMC_IS` enables the Exynos4x12 imaging subsystem, firmware loader, and DMA support. `VIDEO_EXYNOS4_ISP_DMA_CAPTURE` optionally adds ISP direct DMA capture and defaults to enabled when FIMC-IS is selected.

## Control Flow
There is no runtime control flow. Build configuration gates compilation by dependencies on V4L platform drivers, OF, common clock, I2C, DMA, regulator, SoC symbols, and compile-test.

## State and Persistence
Configuration state is persisted in the kernel `.config`. It determines which modules or built-in objects exist but stores no runtime driver state.

## Dependencies and Integration Points
The selections tie this directory into V4L2, media controller, videobuf2 DMA-contig, mem2mem, firmware loading, MFD syscon, fwnode parsing, and platform-specific Exynos/S5PV210 architecture symbols. The `Makefile` consumes these symbols to produce `s5p-fimc`, `s5p-csis`, `exynos-fimc-lite`, `exynos-fimc-is`, and `exynos4-is-common` objects.

## Risks and Edge Cases
Selecting FIMC requires I2C even for configurations primarily using memory-to-memory operation. FIMC-IS depends on external firmware and setfile assets at runtime, which Kconfig cannot validate. `COMPILE_TEST` can build drivers outside native platforms, so probe paths must handle missing DT resources gracefully.

## Test Signals
Important signals are `allyesconfig`/`allmodconfig` build coverage, module names matching help text, dependency failures when required subsystems are absent, successful compile-test on non-Exynos architectures, and optional inclusion/exclusion of `fimc-isp-video.o` through `VIDEO_EXYNOS4_ISP_DMA_CAPTURE`.
