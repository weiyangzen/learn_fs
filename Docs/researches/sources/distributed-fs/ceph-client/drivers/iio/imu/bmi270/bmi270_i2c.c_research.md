# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_i2c.c

Purpose: I2C transport wrapper for BMI260/BMI270 core.

Important APIs, types, and functions: local `bmi270_i2c_regmap_config` uses 8-bit register and value fields. `bmi270_i2c_probe()` obtains chip info from I2C/ACPI/OF match data, initializes an I2C regmap, and calls `bmi270_core_probe()`. Device tables provide I2C IDs, ACPI workarounds, and OF compatibles.

Control flow: matched I2C device supplies `chip_info`; probe fails with `-ENODEV` if match data is missing, then delegates to core for firmware load and IIO setup.

State and persistence: no transport-private runtime state beyond managed regmap.

Dependencies and integration: depends on I2C, regmap I2C, BMI270 core PM ops, ACPI IDs `BMI0160`/`BMI0260`, and OF compatibles `bosch,bmi260`/`bosch,bmi270`.

Risks: ACPI `BMI0160` is intentionally mapped to BMI260 for specific devices, while core rejects real BMI160 to avoid misbinding. Firmware files are still required after transport probe succeeds.

Test signals: I2C ID, OF, and ACPI match paths; missing match data; regmap init failure; BMI160 rejection in core; firmware load path; PM callback wiring.
