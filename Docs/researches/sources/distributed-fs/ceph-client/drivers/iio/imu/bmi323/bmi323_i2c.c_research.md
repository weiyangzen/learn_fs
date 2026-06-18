## sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_i2c.c

Purpose: I2C transport wrapper for BMI323. It implements BMI323-specific I2C regmap bus callbacks and delegates all sensor behavior to `bmi323_core_probe()`.

Important APIs, types, and functions: `struct bmi323_i2c_priv` holds the `i2c_client` and a receive buffer large enough for FIFO data plus two dummy bytes. `bmi323_regmap_i2c_read()` issues a two-message I2C transfer, then strips the BMI323-required two dummy bytes. `bmi323_regmap_i2c_write()` writes register-plus-payload through SMBus block write. `bmi323_i2c_regmap_config` is 8-bit register, 16-bit little-endian value, max `BMI323_CFG_RES_REG`.

Control flow: probe allocates transport private data, initializes a devm regmap with the custom bus, and calls the common core probe. Device matching is provided through ACPI `BOSC0200`, I2C ID `bmi323`, and OF compatible `bosch,bmi323`.

State and persistence behavior: no sensor state is kept here beyond the transport buffer and client pointer; runtime PM is delegated by referencing `bmi323_core_pm_ops` in the i2c driver.

Dependencies and integration points: depends on Linux I2C, regmap, module tables, and the exported BMI323 core namespace. The ACPI comment documents an identifier conflict with BMC150 and relies on the core chip-ID check/reset to reject non-BMI323 devices safely.

Risks and edge cases: `i2c_transfer()` success is not checked for a short positive transfer count, only negative errors; a partial positive transfer would still copy from the RX buffer. SMBus block write must support BMI323 payload sizes. Shared ACPI ID can cause attempted probes on other Bosch devices.

Test signals: verify I2C reads strip dummy bytes correctly, writes reach 16-bit little-endian registers, probe fails cleanly on non-BMI323 `BOSC0200`, and runtime suspend/resume callbacks from the core operate through the I2C regmap.
