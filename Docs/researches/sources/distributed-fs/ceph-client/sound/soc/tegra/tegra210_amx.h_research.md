# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_amx.h

## Purpose
Defines AMX register offsets, bit fields, RAM capacities, auto-disable offsets, and private data structures for the Tegra AMX multiplexer driver.

## APIs, Types, and Functions
The header lists RX/TX CIF, interrupt, enable/reset/status/control, byte-enable, CYA, CFG RAM, and frame-period registers for Tegra210, Tegra194, and Tegra264. It defines control masks for master RX selection and RX dependency, RAM write sequencing bits, soft reset bits, channel stride, RAM depth, byte-mask count, max channel count, and `TEGRA_AMX_OUT_DAI_ID`. `enum` values model wait-on-all vs wait-on-any behavior. `struct tegra210_amx_soc_data` parameterizes regmap config, auto-disable, extra controls, max channels, RAM depth, mask size, and register offset. `struct tegra210_amx` stores regmap and software map/mask state.

## Control Flow, State, and Persistence
No executable code is present. Constants here control probe allocations, regmap bounds, resume-time RAM writes, auto-disable register programming, and shared DAI mutation. The software map/mask state in the C file mirrors hardware RAM whose contents need explicit restoration.

## Dependencies and Integration
Depends on ASoC/regmap types through includers. Integrates with AMX implementation and AHUB route names for RX1-RX4 and TX endpoints.

## Risks and Test Signals
Risks include stale DAI ID assumptions, wrong Tegra264 `reg_offset`, frame-period range omissions, and mismatched RAM depth versus exposed byte-map controls. Test signals include successful access to SoC-specific CFG RAM addresses, correct number of byte-mask registers written, and max-channel behavior matching SoC data.
