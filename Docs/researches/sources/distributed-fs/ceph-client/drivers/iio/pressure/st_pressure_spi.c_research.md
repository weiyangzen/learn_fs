<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_spi.c

## Purpose
`st_pressure_spi.c` is the SPI bus wrapper for STMicroelectronics pressure sensors. It maps SPI modalias/OF compatibles to common settings, configures the generic ST SPI transport, enables power, and invokes the common pressure core.

## Important APIs, types, and functions
OF match entries include both legacy `*-press` and newer single-chip compatible strings. `st_press_spi_probe()` normalizes `spi->modalias`, looks up settings, allocates `struct st_sensor_data`, calls `st_sensors_spi_configure()`, enables power, and calls `st_press_common_probe()`. SPI ID table includes modern names and legacy aliases.

## Control flow
The SPI core calls probe; the wrapper resolves the correct settings and transport configuration before delegating to the core for WAI verification, channel setup, triggers, buffers, and IIO registration.

## State and persistence behavior
No separate wrapper state exists beyond common `st_sensor_data`. Hardware power and transport configuration are managed through the generic ST layer.

## Dependencies and integration points
It depends on Linux SPI, OF/SPI ID matching, `st_sensors_spi_configure()`, `st_sensors_power_enable()`, and namespace `IIO_ST_SENSORS`.

## Risks
SPI modalias normalization must preserve compatibility with legacy names. SPI bus mode/multiread behavior is encoded in the settings and generic ST SPI layer, so variant table errors surface as communication failures. Unsupported aliases fail early.

## Test signals
Probe all SPI IDs and OF compatibles, including legacy `lps25h-press` style aliases, inject SPI configure/power failures, and run common ST pressure direct and buffered tests over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_spi.c -->
