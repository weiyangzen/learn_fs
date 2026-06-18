# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Kconfig

## Purpose
This Kconfig fragment exposes bus-specific ST LIS3LV02Dx accelerometer drivers for SPI and I2C.

## Important APIs, types, and functions
`CONFIG_SENSORS_LIS3_SPI` builds the SPI transport and selects the shared `SENSORS_LIS3LV02D` core. It depends on `!ACPI`, `SPI_MASTER`, and `INPUT`. `CONFIG_SENSORS_LIS3_I2C` builds the I2C transport, depends on `I2C` and `INPUT`, and also selects the shared core.

## Control flow
The file only controls build configuration. Selecting either bus driver pulls in the common accelerometer core that provides sysfs, input, misc freefall, and shared sensor logic.

## State and persistence
No runtime state exists. The tristate choices determine whether `lis3lv02d.o`, `lis3lv02d_spi.o`, and/or `lis3lv02d_i2c.o` are built in or as modules.

## Dependencies and integration points
The options reflect runtime integration with SPI/I2C bus subsystems and the input subsystem. The SPI driver excludes ACPI, while the I2C path can be used with platform data or OF.

## Risks
Incorrect dependencies could build transport code without input or bus symbols. Because both transports select the same singleton core, configurations enabling both should be considered carefully in runtime tests.

## Test signals
Build matrix tests should validate SPI-only, I2C-only, both-as-modules, and both-built-in configurations. Help text should match module names `lis3lv02d`, `lis3lv02d_spi`, and `lis3lv02d_i2c`.
