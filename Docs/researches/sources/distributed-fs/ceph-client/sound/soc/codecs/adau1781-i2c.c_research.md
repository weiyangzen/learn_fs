# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-i2c.c

## Purpose
I2C transport glue for ADAU1381/ADAU1781 ASoC codecs.

## APIs, Types, and Functions
`adau1781_i2c_probe()` copies `adau1781_regmap_config`, sets 8-bit values and 16-bit register addresses for I2C, creates a devm I2C regmap, and calls `adau1781_probe()` with match data. `adau1781_i2c_remove()` calls `adau17x1_remove()` for clock cleanup. The file registers I2C IDs for `adau1381` and `adau1781`, optional OF compatible strings, and an `i2c_driver` via `module_i2c_driver()`.

## Control Flow, State, and Persistence
All persistent codec state is allocated by `adau17x1_probe()` in the core path. The I2C file only adapts probe/remove and device matching. There is no explicit I2C remove state beyond disabling any prepared optional `mclk`.

## Dependencies and Integration
Depends on Linux I2C, regmap, mod_devicetable, and the shared ADAU1781 header. It integrates with device tree compatible strings `adi,adau1381` and `adi,adau1781`, plus legacy I2C ID matching.

## Risks and Test Signals
Risk is match data mismatch: the OF table entries omit `.data`, so `i2c_get_match_data()` must be checked against kernel matching behavior and fallback ID matching for the targeted tree. Test signals are successful I2C probe, correct type selection, regmap bus transactions with 16-bit registers, and removal without leaked prepared clocks.
