# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_i2c.c

Purpose: I2C transport driver for ADXL312/ADXL313/ADXL314. It creates variant-specific regmaps and delegates all IIO behavior to the ADXL313 core.

Important APIs/types/functions: `adxl31x_i2c_regmap_config[]` selects register access tables, volatile callback, max register, 8-bit register/value widths, and Maple regcache per chip type. Match tables are `adxl313_i2c_id` and `adxl313_of_match`. `adxl313_i2c_probe()` obtains `struct adxl313_chip_info`, initializes regmap, and calls `adxl313_core_probe()`.

Control flow: device matching provides chip info, probe creates an I2C regmap indexed by `chip_data->type`, reports regmap errors, then invokes the core with no extra setup callback.

State and persistence: the frontend has no private runtime state after probe. Regmap cache and hardware state are owned by the core and devm-managed resources.

Dependencies and integration: depends on I2C, OF matching, regmap I2C, and exported `IIO_ADXL313` symbols. Kconfig selects `ADXL313` and `REGMAP_I2C`.

Risks: `i2c_get_match_data()` must return non-NULL chip data; the code assumes it. Wrong match data type would index the regmap config array incorrectly.

Test signals: I2C and OF modalias binding for all three compatible strings, regmap initialization, core probe success, raw read over I2C, and module namespace import resolution.
