# sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Kconfig

## Purpose
Kconfig menu for digital potentiostat drivers.

## Important APIs, Types, And Functions
Defines `CONFIG_LMP91000` for the Texas Instruments LMP91000 potentiostat driver. It depends on I2C and selects `REGMAP_I2C`, `IIO_BUFFER`, `IIO_BUFFER_CB`, and `IIO_TRIGGERED_BUFFER`.

## Control Flow
Enabling the option builds `lmp91000.o` via the Makefile. Help text documents module name `lmp91000`.

## State And Persistence
No runtime state; build-time selection only.

## Dependencies And Integration Points
Ensures the potentiostat driver has regmap and buffered IIO support.

## Risks And Test Signals
Build-test module and built-in configurations to confirm selected buffer dependencies cover the driver.
