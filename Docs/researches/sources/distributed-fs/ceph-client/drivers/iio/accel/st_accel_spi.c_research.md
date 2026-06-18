# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_spi.c

Purpose: SPI transport wrapper for the shared ST accelerometer core.

Important APIs/types/functions: the OF table maps supported SPI-compatible strings to canonical device names. The SPI id table lists modalias names. `st_accel_spi_probe()` normalizes `spi->modalias`, retrieves settings through `st_accel_get_settings()`, allocates the IIO device, records settings in `struct st_sensor_data`, configures SPI bus access via `st_sensors_spi_configure()`, enables power, and calls `st_accel_common_probe()`.

Control flow: `module_spi_driver()` registers the wrapper. Probe is intentionally thin: bus identification and access setup happen locally, while chip-id verification, channel assignment, register initialization, buffer setup, trigger setup, and IIO registration are delegated to the core.

State and persistence behavior: no wrapper-specific persistent state. The shared ST sensor state is allocated as IIO private data, and hardware register state is managed by the common core and ST helpers.

Dependencies and integration points: depends on SPI, OF modalias matching, `st_sensors_spi_configure()`, `st_sensors_power_enable()`, and the exported core functions in the `IIO_ST_SENSORS` namespace.

Risks: SPI support lacks ACPI matching unlike the I2C wrapper. Compatible strings need careful maintenance for old `*-accel` names and newer single-chip names. Some ST parts have bus-specific quirks such as SIM and multiread settings; incorrect settings-table values surface through this wrapper.

Test signals: compile with SPI support, bind through SPI id and OF compatible strings, validate unknown modalias rejection, inject SPI configuration and power failures, and run common ST raw, scale, ODR, and triggered-buffer tests over SPI.
