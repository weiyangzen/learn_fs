# sources/distributed-fs/ceph-client/sound/soc/adi/Kconfig

## Purpose
`sound/soc/adi/Kconfig` declares ASoC driver options for Analog Devices AXI softcore audio peripherals.

## Important APIs, Types, And Functions
The file defines `SND_SOC_ADI_AXI_I2S` for the AXI-I2S peripheral and `SND_SOC_ADI_AXI_SPDIF` for the AXI-SPDIF transmitter. Both are tristates and select `SND_SOC_GENERIC_DMAENGINE_PCM` and `REGMAP_MMIO`.

## Control Flow
There is no runtime flow. When either symbol is selected, kbuild includes the matching object from `sound/soc/adi/Makefile`, and the driver gets generic DMAengine PCM plus MMIO regmap support.

## State And Persistence
The persistent state is kernel configuration. Runtime state is held by the selected platform driver.

## Dependencies And Integration Points
This menu is sourced from the top-level ASoC Kconfig. Its symbols build `axi-i2s.c` and `axi-spdif.c`, which register OF platform drivers and ASoC components.

## Risks And Edge Cases
Both drivers depend on DMAengine and MMIO regmap helpers by selection rather than explicit user choice. Device-tree bindings must provide resources, clocks, and DMA names that match the corresponding driver expectations.

## Test Signals
Build tests should cover module and built-in combinations, and DT-based boot tests should confirm the selected drivers probe only when compatible nodes and required resources exist.
