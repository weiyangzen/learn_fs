# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-i2c.c

## Purpose
I2C bus wrapper for the ADAU1372 codec core. It creates an I2C regmap with the shared ADAU1372 configuration and delegates all codec setup to `adau1372_probe()`.

## Important APIs, Types, and Functions
`adau1372_i2c_probe()` calls `adau1372_probe(&client->dev, devm_regmap_init_i2c(...), NULL)`. The ID table contains `"adau1372"`, and the I2C driver uses the shared `adau1372_of_match` table.

## Control Flow
I2C probe is a one-step delegation. There is no remove callback because all resources are devm-managed and the shared component handles bias/power callbacks.

## State and Persistence
No local state. The core stores private state on the device and owns regcache behavior.

## Dependencies and Integration Points
Depends on I2C, regmap, ASoC headers, and `adau1372.h`. It binds both legacy I2C ID and OF compatible devices.

## Risks
Any I2C regmap initialization error is propagated through the core's `IS_ERR(regmap)` check. I2C mode does not need a switch-mode callback, unlike SPI.

## Test Signals
I2C probe, OF match with `adi,adau1372`, register access with 16-bit addresses/8-bit values, and shared-core DAI/control registration.
