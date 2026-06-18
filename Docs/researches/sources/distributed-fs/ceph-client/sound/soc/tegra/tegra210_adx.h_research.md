# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_adx.h

## Purpose
Defines ADX register offsets, CFG RAM control bits, capacity constants, and private state structures for the Tegra ADX demultiplexer driver.

## APIs, Types, and Functions
The header provides RX/TX CIF and interrupt register offsets, module enable/reset/status/control registers, byte-enable registers, CFG RAM registers, and Tegra264 shifted CYA/CFG RAM offsets. It defines RAM access bits (`RW_WRITE`, `ADDR_INIT_EN`, `SEQ_ACCESS_EN`), soft-reset bits, channel stride, RAM depth, byte-mask count, max channel count, CYA offset, and `TEGRA_ADX_IN_DAI_ID`. `struct tegra210_adx_soc_data` parameterizes regmap config, extra controls, max channels, RAM depth, byte-mask size, and offset. `struct tegra210_adx` stores regmap plus software copies of map RAM and byte masks.

## Control Flow, State, and Persistence
There is no executable flow. The map RAM constants determine how many software entries are allocated and how many writes `tegra210_adx_write_map_ram()` performs during resume. The DAI ID constant is used to mutate the shared DAI definition to match SoC channel capacity.

## Dependencies and Integration
Depends on regmap and ASoC control types through includers. It integrates with ADX C implementation and AHUB route names for ADX RX/TX ports.

## Risks and Test Signals
Risks include offset confusion between Tegra210 and Tegra264, RAM depth and byte-mask count mismatches, and stale `TEGRA_ADX_IN_DAI_ID` if the DAI array order changes. Test signals include successful register access on both compatibles, correct number of byte-map controls, and resume programming the expected RAM depth.
