# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_i2c.c

Purpose: I2C frontend for ADXL345 and ADXL375 accelerometers.

Important APIs/types/functions: `adxl345_i2c_regmap_config` defines 8-bit register/value access, volatile callback, and Maple regcache. `adxl345_i2c_info` and `adxl375_i2c_info` provide names and scale constants. Match tables cover I2C IDs, OF compatibles, and ACPI ID `ADS0345`. `adxl345_i2c_probe()` initializes regmap and calls the core.

Control flow: probe creates a devm I2C regmap, returns a dev_err_probe message on failure, and invokes `adxl345_core_probe(&client->dev, regmap, false, NULL)`. The `false` FIFO-delay flag reflects I2C timing being slow enough for FIFO pop requirements.

State and persistence: no I2C-private state persists after probe. Regmap and all sensor state are devm/core-owned.

Dependencies and integration: depends on I2C, regmap I2C, OF/ACPI matching, and `IIO_ADXL345` core exports. Kconfig excludes the older input driver and selects `ADXL345` plus `REGMAP_I2C`.

Risks: core obtains chip info via `device_get_match_data()`, so all match paths must carry the correct data pointer. ACPI match only names ADXL345 scale.

Test signals: I2C/OF/ACPI binding, regmap creation, core device ID validation, raw data reads, no FIFO delay behavior, and ADXL345/ADXL375 scale selection.
