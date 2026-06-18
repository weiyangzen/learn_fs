<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-spi.c

Purpose: SPI bus front end and custom regmap bus for BMP280-family sensors.

Important APIs, types, and functions: `bmp280_regmap_spi_write()` clears bit 7 for write commands and performs a two-byte SPI transaction. `bmp280_regmap_spi_read()` uses basic SPI read. `bmp380_regmap_spi_read()` handles BMP3xx/BMP5xx-style reads by discarding the first returned dummy byte. `bmp280_spi_probe()` selects the regmap bus based on `chip_info->spi_read_extra_byte`, initializes regmap, and calls `bmp280_common_probe()`.

Control flow: match tables map SPI/OF IDs to chip-info. Probe builds a regmap with either normal BMP280 or extra-byte BMP380 bus semantics, then hands off all IIO behavior to the core.

State and persistence: no SPI-private state persists beyond the devm regmap. Temporary read buffers are stack local.

Dependencies and integration points: depends on SPI, custom regmap bus callbacks, chip-info exports, common PM ops, and namespace `IIO_BMP280`.

Risks: write callback copies exactly two bytes from regmap data, so it assumes 8-bit register plus 8-bit value writes. `bmp380_regmap_spi_read()` limits reads to `BME280_BURST_READ_BYTES`, which must remain large enough for all SPI bulk reads using the extra-byte protocol. SPI mode and max speed are not validated in code. ID table includes `bmp181` alias mapping to BMP180 only on SPI.

Test signals: logic-analyzer verification of read/write command framing, BMP380/BMP580 dummy-byte reads, bulk read length rejection, all compatible mappings, and common-core runtime PM through SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-spi.c -->
