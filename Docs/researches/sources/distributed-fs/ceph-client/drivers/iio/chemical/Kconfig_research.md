# sources/distributed-fs/ceph-client/drivers/iio/chemical/Kconfig

## Purpose
This Kconfig menu declares chemical and air-quality IIO sensor drivers, including the subset's AGS02MA, Atlas, BME680, CCS811, ENS160, iAQ-Core, MH-Z19B, PMS7003, and SCD30 symbols.

## Important APIs, Types, And Functions
Relevant symbols include `AOSONG_AGS02MA`, `ATLAS_PH_SENSOR`, `ATLAS_EZO_SENSOR`, `BME680`, `BME680_I2C`, `BME680_SPI`, `CCS811`, `ENS160`, `ENS160_I2C`, `ENS160_SPI`, `IAQCORE`, `MHZ19B`, `PMS7003`, `SCD30_CORE`, `SCD30_I2C`, and `SCD30_SERIAL`. It also includes other chemical drivers outside this work item.

## Control Flow
There is no runtime control flow. Kconfig dependency and `select` statements determine bus support, regmap support, CRC helpers, serial bus support, IIO buffering, and triggered-buffer helper availability.

## State And Persistence
Kernel configuration persists symbol selections and controls which modules or built-ins are produced.

## Dependencies And Integration Points
The file integrates with the sibling Makefile, bus frameworks (`I2C`, `SPI`, `SERIAL_DEV_BUS`), `REGMAP`, `CRC8`/`CRC16`, `IIO_BUFFER`, and `IIO_TRIGGERED_BUFFER`.

## Risks
Core/transport split symbols must select the right transport support. `ENS160_I2C` and `ENS160_SPI` select regmap transports but do not explicitly depend on `ENS160`; they are selected by `ENS160` when buses are present. Missing buffer selects would break drivers using `devm_iio_triggered_buffer_setup()`.

## Test Signals
Run randconfig and targeted builds for each bus combination, especially `BME680` with only I2C or only SPI and `ENS160` with transport modules.
