<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/Kconfig

## Purpose
Kconfig menu for Socionext UniPhier ASoC support. It exposes the common AIO CPU DAI driver, LD11/LD20 and PXs2 device drivers, and the internal EVEA codec driver.

## APIs, Types, and Functions
Defines `SND_SOC_UNIPHIER_AIO`, `SND_SOC_UNIPHIER_LD11`, `SND_SOC_UNIPHIER_PXS2`, and `SND_SOC_UNIPHIER_EVEA_CODEC`. The menu depends on `ARCH_UNIPHIER || COMPILE_TEST`; AIO selects `REGMAP_MMIO` and `SND_SOC_COMPRESS`; SoC device drivers select the common AIO driver; EVEA selects `REGMAP_MMIO`.

## Control Flow, State, and Persistence
This file controls build-time availability only. Selecting LD11 or PXs2 pulls in the shared AIO CPU/compress/core objects; selecting EVEA builds the internal codec independently.

## Dependencies and Integration
Integrates with the kernel ASoC Kconfig hierarchy and corresponding Makefile object names. It enables compile-test coverage outside UniPhier architectures.

## Risks and Test Signals
Risks include missing dependencies for reset/clk/syscon/DMA symbols if not selected elsewhere and broad `SND_SOC_COMPRESS` selection whenever AIO is enabled. Test signals are `allyesconfig`, `COMPILE_TEST`, module builds for each option, and dependency resolution in minimal UniPhier configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/Kconfig -->
