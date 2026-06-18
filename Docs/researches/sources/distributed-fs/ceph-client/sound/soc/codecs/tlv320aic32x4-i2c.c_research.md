# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic32x4-i2c.c

## Purpose
Provides the I2C transport wrapper for the TLV320AIC32x4/TLV320AIC32x6/TAS2505 shared codec core.

## Important APIs, Types, and Functions
`aic32x4_i2c_probe()` copies `aic32x4_regmap_config`, sets 8-bit register and value widths, creates an I2C regmap, extracts the matched `enum aic32x4_type`, and calls `aic32x4_probe()`. `aic32x4_i2c_remove()` delegates to `aic32x4_remove()`. The I2C and OF ID tables map device names and compatibles to codec variants.

## Control Flow
The `module_i2c_driver()` registration binds matching I2C devices. Probe creates the bus regmap and immediately hands all hardware setup to the shared core. Remove performs only shared core cleanup, mainly regulator disable.

## State and Persistence
This file owns no long-lived state besides the devm regmap object and match data. All codec state lives in the common driver private data attached to `i2c->dev`.

## Dependencies and Integration Points
Depends on Linux I2C, regmap, OF matching, and ASoC module registration. Integrates with `tlv320aic32x4.c` through exported `aic32x4_probe()`, `aic32x4_remove()`, and `aic32x4_regmap_config`.

## Risks
Regmap creation errors are not checked locally, but the shared probe checks `IS_ERR(regmap)`. OF table entries include variant data, while SPI lacks TAS2505 support; board compatibility must choose the proper bus wrapper. Match-data availability is required for correct variant behavior.

## Test Signals
Probe each compatible string over I2C, verify regmap read/write framing, confirm TAS2505 selects the TAS component path, and validate deferred probe behavior when shared core regulators or clocks are missing.
