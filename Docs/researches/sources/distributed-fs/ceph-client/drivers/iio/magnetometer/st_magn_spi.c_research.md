# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_spi.c

## Purpose
SPI transport glue for the common ST magnetometer driver.

## Important APIs, Types, And Functions
`st_magn_of_match[]` lists SPI-capable ST magnetometers and maps compatibles to common device names. `st_magn_spi_probe()` normalizes `spi->modalias`, finds common settings, allocates IIO private ST state, configures SPI transport through `st_sensors_spi_configure()`, enables power, and calls `st_magn_common_probe()`. `st_magn_id_table[]` exposes SPI modalias support.

## Control Flow
The probe path mirrors I2C: identify settings, allocate IIO state, configure bus operations, enable power, and delegate to common probe. Older I2C-only parts are intentionally absent from the SPI ID table.

## State And Persistence
No persistent state. Runtime configuration and data-ready behavior are controlled by the common ST core and hardware registers.

## Dependencies And Integration Points
Depends on `linux/iio/common/st_sensors_spi.h`, ST common sensor helpers, and `st_magn_core.c`.

## Risks And Test Signals
Compatibility-string naming is subtle for single-chip vs multi-function devices. Test SPI modalias and OF matching, sensor ID verification through the SPI regmap path, and scale/ODR/buffer operations on each SPI-capable part.
