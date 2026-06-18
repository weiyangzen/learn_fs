# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-i2c.c

## Purpose
I2C bus wrapper for ADAU1977/ADAU1978/ADAU1979 ADC codecs.

## APIs, Types, and Functions
`adau1977_i2c_probe()` copies `adau1977_regmap_config`, sets 8-bit register and value widths for I2C, creates an I2C regmap, and calls `adau1977_probe()` with match data and no mode-switch callback. The I2C ID table maps `adau1977` to `ADAU1977` and both `adau1978` and `adau1979` entries to `ADAU1978` in this source.

## Control Flow, State, and Persistence
All persistent state is in `struct adau1977` allocated by the common probe. This file only performs transport setup and driver registration through `module_i2c_driver()`.

## Dependencies and Integration
Depends on Linux I2C, regmap, ASoC headers, and `adau1977.h`. Integrates with legacy I2C device IDs; this file does not define OF match data, so OF-only systems rely on modalias/I2C board registration elsewhere.

## Risks and Test Signals
Risks include the `adau1979` ID using `ADAU1978` instead of `ADAU1979`, lack of OF table in the I2C wrapper, and match-data dependence. Test signals are probe with each I2C ID, correct component type behavior such as MICBIAS only for ADAU1977, and successful regmap reads/writes with 8-bit addressing.
