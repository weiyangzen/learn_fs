# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_admaif.h

## Purpose
Defines the ADMAIF register layout, per-SoC channel limits, FIFO/CIF defaults, bit fields, and private driver data structures consumed by `tegra210_admaif.c`.

## APIs, Types, and Functions
The header exports register base and limit macros for Tegra210, Tegra186, and Tegra264, common RX/TX/global register offsets, pack-mode and enable/reset bit definitions, and large per-channel FIFO default tables. It defines local enums for sample packing (`DATA_8BIT`, `DATA_16BIT`, `DATA_32BIT`) and ADMAIF paths (`ADMAIF_RX_PATH`, `ADMAIF_TX_PATH`, `ADMAIF_PATHS`). `struct tegra_admaif_soc_data` carries component, regmap, DAI, base-address, channel-count, and max-channel parameters. `struct tegra_admaif` stores DMA metadata arrays, conversion-control arrays, regmap, SoC data, and an isomgr pointer.

## Control Flow, State, and Persistence
This file has no executable control flow. Its constants drive register address calculations in the C file and seed regmap defaults. The default tables matter across runtime PM because the regmap uses flat cache and defaults to restore channel interrupt masks, CIF format defaults, FIFO control defaults, and global clock-gating state.

## Dependencies and Integration
Depends implicitly on kernel `BIT()` definitions and ASoC/regmap types included by the C file before use. It integrates tightly with the ADMAIF component implementation and with hardware documentation for channel stride and FIFO defaults.

## Risks and Test Signals
Risks are off-by-one channel default expansion, incorrect Tegra264 base/limit values, and ABI drift if hardware register definitions change without updating the regmap readable/writeable filters. Test signals include regmap default-count consistency (`channel_count * 6 + 1`), valid FIFO addresses for every advertised DAI, and matching max channel limits between header constants and AHUB route capacity.
