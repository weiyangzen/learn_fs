# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_spi.c

Purpose: SPI frontend for ADXL345 and ADXL375 accelerometers.

Important APIs/types/functions: constants cap SPI at 5 MHz and mark FIFO delay as needed above 1.5 MHz. `adxl345_spi_regmap_config` uses 8-bit register/value access, multi-byte read flags, volatile callback, and Maple regcache. `adxl345_spi_setup()` enables 3-wire SPI mode in DATA_FORMAT. Probe validates speed, initializes regmap, computes `needs_delay`, and calls the core.

Control flow: if `spi->max_speed_hz` exceeds 5 MHz, probe fails. Otherwise it creates an SPI regmap and invokes `adxl345_core_probe()` with a FIFO delay flag based on clock speed and an optional setup callback only when `SPI_3WIRE` is set.

State and persistence: frontend state does not persist beyond SPI mode/regmap setup. The core stores the FIFO delay flag and sensor state.

Dependencies and integration: depends on SPI, regmap SPI, OF/ACPI/SPI ID matching, and `IIO_ADXL345` exports. It imports the core namespace.

Risks: FIFO correctness depends on the speed threshold and `udelay(3)` in the core. 3-wire mode requires a DATA_FORMAT write before normal operation. Board files with excessive `max_speed_hz` are rejected.

Test signals: SPI binding for ADXL345/ADXL375, speed-limit failure, 3-wire setup, high-speed FIFO watermark reads with delay, raw/scale/ODR sysfs, and interrupt events.
