<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-i2c.c

Purpose: I2C bus front end for the Bosch BMP280-family common core.

Important APIs, types, and functions: `bmp280_i2c_probe()` obtains the matched `bmp280_chip_info`, initializes an I2C regmap from the chip-specific regmap config, and calls `bmp280_common_probe()`. OF and I2C ID tables map BMP085, BMP180, BMP280, BME280, BMP380, and BMP580 names to exported chip-info structures.

Control flow: all runtime operations after probe are delegated to the common core through regmap. The adapter passes `client->irq` so core code can configure BMP085 EOC or BMP380/BMP580 data-ready triggers when available.

State and persistence: no I2C-private state is allocated. The regmap and IIO state are devm-managed through the common probe.

Dependencies and integration points: depends on I2C, regmap I2C, PM ops from the core, and namespace `IIO_BMP280`. Kconfig selects this helper when BMP280 and I2C are enabled.

Risks: `id->name` is used for the IIO name, so OF-only devices still depend on an I2C ID being available from the client. There is no explicit I2C functionality check, relying on `devm_regmap_init_i2c()` and bus core behavior. Match table drift can cause a compatible to select the wrong compensation path.

Test signals: probe every compatible/ID mapping, verify IRQ forwarding, build as module with namespace import, and exercise regmap failure handling on unsupported adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-i2c.c -->
