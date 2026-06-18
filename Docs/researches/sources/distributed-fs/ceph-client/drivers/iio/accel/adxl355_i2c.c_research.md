# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_i2c.c

Purpose: I2C frontend for ADXL355 and ADXL359 accelerometers.

Important APIs/types/functions: `adxl355_i2c_regmap_config` uses 8-bit register/value access, max register `0x2F`, and core-exported readable/writeable access tables. Match tables cover I2C IDs and OF compatibles for `adi,adxl355` and `adi,adxl359`. `adxl355_i2c_probe()` selects chip data, creates regmap, and calls the core.

Control flow: probe rejects missing match data, initializes devm I2C regmap, reports regmap errors, then delegates to `adxl355_core_probe()`.

State and persistence: no frontend-private state persists. Regmap and IIO resources are devm-managed by the core/frontend combination.

Dependencies and integration: depends on I2C, regmap I2C, OF matching, and `IIO_ADXL355` exports. Kconfig selects `ADXL355`, `REGMAP_I2C`, `IIO_BUFFER`, and `IIO_TRIGGERED_BUFFER`.

Risks: missing or wrong match data causes either `-ENODEV` or incorrect scale/part validation. Access tables must match the 8-bit I2C protocol.

Test signals: I2C/OF binding for both variants, regmap initialization, core reset/ID validation, raw and triggered-buffer reads, and module namespace import resolution.
