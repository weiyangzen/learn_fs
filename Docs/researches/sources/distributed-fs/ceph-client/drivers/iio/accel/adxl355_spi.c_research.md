# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_spi.c

Purpose: SPI frontend for ADXL355 and ADXL359 accelerometers.

Important APIs/types/functions: `adxl355_spi_regmap_config` models the SPI protocol with 7 register bits, 1 pad bit, 8 value bits, read flag `BIT(0)`, max register `0x2F`, and core-exported access tables. Match tables cover SPI IDs and OF compatibles. `adxl355_spi_probe()` selects chip data, initializes SPI regmap, and calls the core.

Control flow: probe gets match data through `spi_get_device_match_data()`, rejects missing data, creates a devm SPI regmap, reports regmap errors, and delegates to `adxl355_core_probe()`.

State and persistence: no frontend-private state persists beyond regmap/probe resources. Sensor state and buffers are core-owned.

Dependencies and integration: depends on SPI, regmap SPI, OF/SPI ID matching, and `IIO_ADXL355` exports. It imports namespace `IIO_ADXL355`.

Risks: SPI register framing differs from I2C; wrong `reg_bits`, `pad_bits`, or read flag would corrupt every register access. Missing match data fails probe with `-EINVAL`.

Test signals: SPI binding for both variants, register read/write sanity, core setup and shadow-register reset, DRDY trigger operation, raw sysfs reads, and buffered capture.
