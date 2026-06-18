# sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm-fuse.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm-fuse.c` computes Tegra SOCTHERM calibration words from SoC efuse fields. The common SOCTHERM driver calls it during probe before enabling raw sensors. The source was read as a complete 166-line file.

## Important APIs, Types, and Functions

The exported internal helpers are `tegra_calc_shared_calib()` and `tegra_calc_tsensor_calib()`. `div64_s64_precise()` is a local rounding helper used to avoid coarse truncation in fixed-point calibration math. It consumes `struct tegra_soctherm_fuse`, `struct tsensor_shared_calib`, and per-sensor `struct tegra_tsensor` metadata from `soctherm.h`.

## Control Flow

`tegra_calc_shared_calib()` reads the SoC common fuse register through `tegra_fuse_readl()`, extracts base CP/FT and shift CP/FT fields using the descriptor masks, optionally reads a spare realignment register for pre-Tegra210 layouts, sign-extends shift fields, and computes actual cold-point and factory-test temperatures. `tegra_calc_tsensor_calib()` reads each sensor fuse, derives actual sensor CP/FT values, calculates slope/intercept (`therma`, `thermb`) adjusted by sample and pdiv ratios, applies per-sensor correction coefficients, and packs the result into `SENSOR_CONFIG2_THERMA/THERMB` bitfields.

## State and Persistence Behavior

The file has no persistent state. It reads immutable fuse values and returns computed calibration words to the caller, which stores them in the driver's `tegra->calib[]` array and later writes sensor registers.

## Dependencies and Integration Points

It depends on `soc/tegra/fuse.h`, `div64_s64()`, `sign_extend32()`, and layout constants shared in `soctherm.h`. The SoC descriptor files provide masks, shifts, nominal FT temperatures, sensor fuse offsets, correction coefficients, pdiv values, and sampling parameters.

## Risks and Edge Cases

Fuse bitfield definitions are hardware ABI. A mask/shift error corrupts all temperatures for an SoC. The code performs signed fixed-point divisions where `delta_sens` and `delta_temp` must be valid; malformed fuses could cause invalid slopes. The `shifted_cp` path sign-extends from `val` after masking/extracting, so this logic should be reviewed carefully for each fuse layout. Rounding changes can alter thermal behavior and trip timing.

## Test Signals

Strong signals include boot-time calibration values compared against vendor tables, unit tests with known fuse vectors for Tegra114/124/132/210 layouts, sensor temperature sanity under ambient conditions, and probe failure coverage for `tegra_fuse_readl()` errors.
