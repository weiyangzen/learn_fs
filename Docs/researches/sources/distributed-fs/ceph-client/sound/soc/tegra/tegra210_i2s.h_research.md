# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_i2s.h

## Purpose
Defines I2S register offsets, SoC-specific register-layout deltas, bit masks, default slot/FIFO settings, path enums, and private state structures used by the Tegra I2S driver.

## APIs, Types, and Functions
The header lists Tegra210 RX/TX/common register offsets and Tegra264-specific shifted TX/common/PIO/pad status registers. It defines control fields for data offset, fsync width, enable, clock edge, frame format, master mode, LRCK polarity, loopback, sample size, timing bit count, and soft reset. It also defines FIFO depth, default FIFO threshold, slot masks, TX/control offsets, and max channel counts. `enum tegra210_i2s_path` indexes RX/TX conversion arrays. `struct tegra_i2s_soc_data` holds regmap/component pointers and layout/capacity parameters. `struct tegra210_i2s` stores clocks, regmap, conversion settings, DAI format, fsync/BCLK/TDM/FIFO state, and loopback.

## Control Flow, State, and Persistence
No executable code is present. Constants here drive regmap bounds, stream reset register selection, bit-clock/timing computation, slot-mask clamping, and Tegra264 offset handling. State fields are mostly software control caches that are applied during `set_fmt`, `hw_params`, or mixer-control updates and then restored through regmap cache on runtime resume.

## Dependencies and Integration
Depends on clock and regmap types through includers. Integrates with `tegra210_i2s.c`, `tegra_cif`, simple-card graph conversion parsing, and AHUB XBAR routes.

## Risks and Test Signals
Risks include incorrect Tegra264 offsets, fsync-width mask width differences, slot-mask truncation when TDM channels exceed SoC width, and path enum misuse in conversion controls. Test signals include register access validation for both SoCs, correct max channel advertising, fsync-width programming at bit positions 24 vs 23, and valid reset/enable status polling on shifted Tegra264 TX registers.
