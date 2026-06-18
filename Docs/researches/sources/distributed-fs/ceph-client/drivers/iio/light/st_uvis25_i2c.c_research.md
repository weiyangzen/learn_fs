# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_i2c.c

## Purpose
`st_uvis25_i2c.c` is the I2C transport wrapper for the ST UVIS25 driver. It creates an I2C regmap with the device's auto-increment flag and delegates all sensor logic to `st_uvis25_probe()`.

## Important APIs, types, and functions
- `st_uvis25_i2c_regmap_config` uses 8-bit registers and values and sets both read and write auto-increment masks to bit 7.
- `st_uvis25_i2c_probe()` initializes the regmap with `devm_regmap_init_i2c()` and calls `st_uvis25_probe(&client->dev, client->irq, regmap)`.
- I2C and OF match tables bind `uvis25` and `st,uvis25`.
- The I2C driver uses `pm_sleep_ptr(&st_uvis25_pm_ops)` and imports the `IIO_UVIS25` namespace.

## Control flow
The I2C core matches an ID or device-tree compatible string, invokes probe, and the wrapper creates a managed regmap. If regmap initialization fails, probe reports the transport error. Otherwise, control transfers to the shared core, which handles WHOAMI, IIO registration, optional IRQ setup, and PM behavior.

## State and persistence
The wrapper owns no runtime state beyond the managed regmap. Sensor state is in the common `struct st_uvis25_hw` allocated by the core. Register writes persist only in the device until reset or power loss.

## Dependencies and integration points
This file integrates the common UVIS25 core with the Linux I2C subsystem, OF matching, module I2C driver registration, regmap-I2C transport, and shared sleep PM callbacks.

## Risks
- Incorrect auto-increment flags would corrupt multi-byte operations if the core later expands beyond single-byte reads.
- The wrapper assumes `client->irq` accurately represents the data-ready line; invalid IRQ metadata is rejected or handled in the core.
- Namespace import/export must stay aligned with the core.

## Test signals
- I2C probe tests should cover regmap initialization failure and successful delegation to core probe.
- OF and I2C ID modalias tests should verify `st,uvis25` and `uvis25` binding.
- PM build tests should ensure `st_uvis25_pm_ops` remains exported and usable from the I2C module.
