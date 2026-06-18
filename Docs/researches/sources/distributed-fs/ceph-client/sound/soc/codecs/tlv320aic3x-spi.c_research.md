# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic3x-spi.c

## Purpose
Provides the SPI wrapper for the TLV320AIC3x family shared codec driver.

## Important APIs, Types, and Functions
`aic3x_spi_probe()` copies `aic3x_regmap`, applies SPI framing with 7 register bits, 1 pad bit, 8 value bits, and read flag `0x01`, then calls `aic3x_probe()` with `spi_get_device_id()->driver_data`. `aic3x_spi_remove()` delegates to the shared remove path.

## Control Flow
`module_spi_driver()` binds the SPI IDs and OF compatibles. The wrapper logs probe at debug level, creates regmap, and hands off to the shared core. Remove leaves reset handling to `aic3x_remove()`.

## State and Persistence
No transport-specific persistent state beyond devm regmap. The core owns the device-private state.

## Dependencies and Integration Points
Depends on SPI, regmap, OF matching, and the shared AIC3x exported interface. It uses the same model constants as the I2C wrapper.

## Risks
The SPI probe obtains model data from the SPI ID rather than `spi_get_device_match_data()`, so pure OF matching must still provide a matching SPI ID path. Incorrect controller read-flag support would break register access. As with I2C, regmap errors are handled by the shared probe.

## Test Signals
Probe all SPI IDs, validate register framing with read flag, check model-specific DAPM additions, and verify remove leaves non-shared reset asserted when applicable.
