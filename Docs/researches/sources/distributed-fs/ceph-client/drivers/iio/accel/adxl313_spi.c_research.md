# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_spi.c

Purpose: SPI transport driver for ADXL312/ADXL313/ADXL314. It configures SPI mode/regmap access, handles 3-wire/I2C-disable setup, and delegates sensor behavior to the shared core.

Important APIs/types/functions: `adxl31x_spi_regmap_config[]` mirrors variant access tables and uses `read_flag_mask = BIT(7) | BIT(6)` for multi-byte reads. `adxl313_spi_setup()` writes 3-wire mode when requested and disables the I2C interface. `adxl313_spi_probe()` sets `SPI_MODE_3`, initializes regmap, and calls `adxl313_core_probe()`.

Control flow: probe forces mode 3 and calls `spi_setup()`, obtains match data, creates an SPI regmap, and passes `adxl313_spi_setup` to the core so bus-specific DATA_FORMAT/POWER_CTL bits are applied before common ID/range/measurement setup.

State and persistence: no frontend-private state persists. SPI mode, regmap cache, and bus-specific hardware bits persist through the device lifetime.

Dependencies and integration: depends on SPI, regmap SPI, device/OF match tables, and `IIO_ADXL313` exports. Kconfig selects `ADXL313` and `REGMAP_SPI`.

Risks: forcing `SPI_MODE_3` may conflict with board descriptions if they are wrong. `adxl313_spi_setup()` always disables I2C, which is required for SPI operation but must happen in the correct sequence. Multi-byte read flags are protocol-specific.

Test signals: SPI probe for ADXL312/313/314, 3-wire and 4-wire modes, regmap bulk reads of XYZ data, I2C-disable bit verification, and core event/FIFO behavior through SPI.
