## sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_i2c.c

Purpose: I2C wrapper for NXP FXOS8700.

Important APIs, types, and functions: `fxos8700_i2c_probe()` initializes an I2C regmap with `fxos8700_regmap_config`, optionally takes the I2C ID name, and calls `fxos8700_core_probe()` with `use_spi=false`. Match tables include I2C ID `fxos8700`, ACPI `FXOS8700`, and OF compatible `nxp,fxos8700`.

Control flow: device match triggers regmap setup, then common core validation/configuration/registration.

State and persistence behavior: no independent state; all runtime behavior is in the core.

Dependencies and integration points: depends on I2C, regmap_i2c, ACPI/OF match tables, and common FXOS8700 exported symbols.

Risks and edge cases: if there is no I2C ID, the core falls back to default name `fxos8700`. Probe errors log with `dev_err` rather than `dev_err_probe`, so deferred-probe messaging may be less polished.

Test signals: I2C probe via OF, ACPI, and ID table; regmap read/write behavior; name assignment; and clean failure on regmap initialization errors.
