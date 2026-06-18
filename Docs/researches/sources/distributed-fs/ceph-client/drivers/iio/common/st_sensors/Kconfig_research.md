
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Kconfig

## Purpose
This Kconfig file defines internal tristate symbols for the STMicroelectronics common IIO sensor helper modules: I2C transport, SPI transport, and core helper library.

## Important APIs, types, and functions
- `IIO_ST_SENSORS_I2C` selects `REGMAP_I2C`.
- `IIO_ST_SENSORS_SPI` selects `REGMAP_SPI`.
- `IIO_ST_SENSORS_CORE` controls the core helper object.

## Control flow
There is no runtime control flow. Sensor-specific drivers select these symbols to pull common support into the build.

## State and persistence behavior
Kconfig state is build configuration only; it does not create runtime state.

## Dependencies and integration points
The symbols integrate with the kernel build system and with the ST sensor Makefile. I2C/SPI helper symbols select the matching regmap backends so transport configuration files can call `devm_regmap_init_i2c()` or `devm_regmap_init_spi()`.

## Risks and edge cases
These symbols have no prompts and are meant to be selected, not user chosen. Missing selects in sensor-specific drivers will lead to unresolved ST helper symbols or missing regmap support.

## Test signals
Build coverage should verify ST sensor drivers selecting these symbols link correctly for built-in and module combinations, especially with `IIO_BUFFER` and `IIO_TRIGGER` enabled or disabled.
