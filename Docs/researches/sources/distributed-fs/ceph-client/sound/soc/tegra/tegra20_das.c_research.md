# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_das.c

## Purpose
This simple platform driver initializes the Tegra20 Digital Audio Switch. DAS is a mux/crossbar connecting DAP pins and DAC/I2S/AC97 controller endpoints. The driver programs a fixed default routing between DAP1/DAC1 and DAP3/DAC3.

## Important APIs, types, and functions
`struct tegra20_das` only contains a regmap. `tegra20_das_connect_dap_to_dac()` writes a DAP control-select register. `tegra20_das_connect_dac_to_dap()` writes a DAC input/data/clock-select register with the selected DAP for clock and serial data. `tegra20_das_probe()` maps registers, initializes regmap, and programs the default links. `tegra20_das_wr_rd_reg()` defines legal regmap ranges.

## Control flow
Probe allocates state, maps the MMIO resource, creates a cached 32-bit regmap, then writes four default connections: DAP1 to DAC1, DAC1 input/clock from DAP1, DAP3 to DAC3, and DAC3 input/clock from DAP3. No public API is exported for runtime rerouting.

## State and persistence
DAS state is just hardware register programming. Regmap is cached, but there is no runtime PM or explicit restore path in this driver. The fixed routing persists until reset or another agent writes the DAS registers.

## Dependencies and integration points
It depends on DT compatible `nvidia,tegra20-das`, MMIO regmap, and the broader Tegra20 audio topology. Kconfig selects DAS for Tegra20 AC97/I2S users.

## Risks and edge cases
The file comment explicitly says the driver is dumb and does not validate routing. Current code hardcodes a limited default topology and does not support board-specific routes, DAP-to-DAP master/slave setup, or runtime control. Resets after probe could lose routing because no PM restore exists.

## Test signals
Probe on Tegra20, read DAS registers after boot, verify I2S/AC97 paths relying on DAP1/DAC1 and DAP3/DAC3 work, and test behavior after system suspend or controller reset.
