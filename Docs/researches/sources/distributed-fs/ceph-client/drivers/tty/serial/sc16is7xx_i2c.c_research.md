# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_i2c.c

## Purpose
I2C transport wrapper for SC16IS7xx chips. It handles I2C/OF matching, creates per-channel I2C regmaps using the shared core regmap configuration, and delegates all UART behavior to `sc16is7xx_probe()`.

## Important APIs, Types, And Functions
`sc16is7xx_i2c_probe()` obtains match data with `i2c_get_match_data()`, copies `sc16is7xx_regcfg`, sets a per-port regmap name and I2C port-select read/write flag masks, and calls `devm_regmap_init_i2c()`. `sc16is7xx_i2c_remove()` delegates to `sc16is7xx_remove()`. The I2C ID table maps SC16IS740/741/74x/750/752/760/762 names to shared devtypes.

## Control Flow
`module_i2c_driver()` registers the driver. Probe fails with `-ENODEV` if match data is absent. For each UART channel in the variant, it creates a regmap configured with `sc16is7xx_regmap_port_mask(i)` for both reads and writes, then calls the core probe with `i2c->irq`.

## State And Persistence
No persistent state beyond devm-managed regmaps. All long-lived UART state is allocated by the core driver and attached as device driver data.

## Dependencies And Integration Points
Depends on I2C core, regmap-I2C, module device tables, and the SC16IS7xx exported namespace. It shares `sc16is7xx_dt_ids` with the core so DT compatible matching remains centralized.

## Risks
The copied `regmap_config` is mutated in a loop; every per-port field must be set before each `devm_regmap_init_i2c()` call. Incorrect flag masks would address the wrong UART channel on dual-port chips.

## Test Signals
Probe all ID aliases through I2C modalias and OF matching, verify `i2cdetect`-level reachability is not enough without LSR read success in the core, and exercise dual-UART traffic to confirm port mask isolation.
