# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/i2c.c

## Purpose
This file is the I2C transport binding for ZL3073x devices. It allocates the shared core state, creates an I2C regmap, and invokes common probe.

## Important APIs and data
`zl3073x_i2c_probe()` is the probe entry point. The I2C ID table and OF compatible table cover `zl30731` through `zl30735`. `module_i2c_driver()` registers the driver.

## Control flow
Probe calls `zl3073x_devm_alloc()`, initializes `zldev->regmap` with `devm_regmap_init_i2c()` and the exported `zl3073x_regmap_config`, then calls `zl3073x_dev_probe()`.

## State and dependencies
All persistent driver state lives in the shared `zl3073x_dev`; the transport owns only the bus registration and regmap binding. It imports the `ZL3073X` namespace exported by the core.

## Risks and tests
Regmap setup failure must abort before common probe. Tests include OF/I2C ID matching, module namespace checks, probe failure unwinding, and basic register reads over I2C.
