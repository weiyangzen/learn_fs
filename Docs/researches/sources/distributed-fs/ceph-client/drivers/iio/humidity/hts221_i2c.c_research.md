# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_i2c.c

Purpose: I2C transport wrapper for the HTS221 core driver.

Important APIs/types/functions: `hts221_i2c_regmap_config` sets 8-bit registers/values and uses the HTS221 auto-increment bit as both read and write flag mask. `hts221_i2c_probe()` initializes an I2C regmap and calls the shared `hts221_probe()` with device, IRQ, client name, and regmap. Match tables include ACPI `SMO9100`, OF `st,hts221`, and I2C id `hts221`.

Control flow: I2C probe creates the regmap; on success all device initialization is delegated to core. Module registration is via `module_i2c_driver`.

State and persistence: No transport-private state beyond the devm regmap. Device runtime state is owned by core.

Dependencies and integration points: Depends on I2C, `REGMAP_I2C`, shared HTS221 symbols, PM ops from core, and namespace `IIO_HTS221`.

Risks: Auto-increment flag masks affect all regmap operations, so single register accesses must tolerate the flag. The transport does no functionality check itself.

Test signals: Probe over I2C with OF and ACPI ids, verify multi-byte calibration/data reads use auto-increment, and confirm PM callbacks resolve from the core module.
