# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_i2c.c

Purpose: I2C transport wrapper for the BMI160/BMI120 core driver.

Important APIs, types, and functions: `bmi160_i2c_probe()` initializes an I2C regmap with `bmi160_regmap_config`, chooses a device name from I2C ID or `dev_name()`, and calls `bmi160_core_probe(..., use_spi=false)`. Device tables include I2C IDs, ACPI IDs, and OF compatibles.

Control flow: the I2C subsystem matches the device, probe creates managed regmap state, then delegates all hardware initialization and IIO registration to the common core.

State and persistence: no transport-private state beyond managed regmap allocation. Runtime state lives in `struct bmi160_data` in the core.

Dependencies and integration: depends on I2C, regmap I2C, PM ops from the core, ACPI IDs including a documented firmware workaround for `10EC5280`, and OF compatibles `bosch,bmi120`/`bosch,bmi160`.

Risks: ACPI workaround intentionally binds incorrect firmware IDs to BMI160; platform validation is important to avoid stealing devices from a more specific driver. Regmap init failure prevents probe.

Test signals: probe through I2C, ACPI, and OF match paths; verify `use_spi=false` avoids dummy SPI read; test PM callbacks and namespace import.
