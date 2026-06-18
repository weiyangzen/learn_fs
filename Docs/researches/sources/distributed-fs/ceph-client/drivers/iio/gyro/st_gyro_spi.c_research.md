# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_spi.c

## Purpose
SPI bus driver for STMicroelectronics gyroscopes using the shared ST gyro core.

## Important APIs, Types, And Functions
Defines OF match table, `st_gyro_spi_probe`, SPI ID table, and `spi_driver`. Uses `st_sensors_dev_name_probe`, `st_gyro_get_settings`, `st_sensors_spi_configure`, `st_sensors_power_enable`, and `st_gyro_common_probe`.

## Control Flow
Probe normalizes the SPI modalias, finds matching settings, allocates IIO state, configures SPI transfer layer, powers the sensor, and delegates registration to common probe.

## State And Persistence
Bus-local state is `st_sensor_data` with SPI transfer hooks and selected settings. Hardware power remains managed by ST common/devm cleanup paths.

## Dependencies And Integration Points
Depends on SPI, ST sensors common SPI helpers, OF/SPI IDs for supported variants, and shared core exports.

## Risks
Name/settings drift across OF table, SPI ID table, and settings table breaks probe. SPI-specific protocol details are delegated to ST common SPI configuration; future devices may need new settings.

## Test Signals
Probe all SPI IDs/OF compatibles, verify SPI transfer setup and power enable, exercise common raw/scale/ODR/buffer paths over SPI, and test bad modalias failure.
