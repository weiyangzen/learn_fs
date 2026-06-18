# sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_i2c.c

## Purpose
`ens160_i2c.c` is the I2C transport for the ENS160 core.

## Important APIs, Types, And Functions
It defines an 8-bit register/8-bit value regmap config and `ens160_i2c_probe()`, which initializes I2C regmap and calls `devm_ens160_core_probe()` with `client->irq` and name `"ens160"`.

## Control Flow
I2C or OF matching invokes probe, which creates regmap and delegates all device initialization to the core. Sleep PM uses shared `ens160_pm_ops`.

## State And Persistence
No transport-specific state is kept beyond devm regmap lifetime.

## Dependencies And Integration Points
It depends on I2C, regmap-I2C, OF/I2C ID tables, shared ENS160 core API, and imports namespace `IIO_ENS160`.

## Risks
The transport passes a fixed name rather than ID-derived name. Regmap init failure is propagated with `dev_err_probe()`. Build correctness depends on Kconfig selecting `REGMAP_I2C`.

## Test Signals
Test I2C/OF match, regmap failure, IRQ forwarding, sleep PM linkage, and module namespace import.
