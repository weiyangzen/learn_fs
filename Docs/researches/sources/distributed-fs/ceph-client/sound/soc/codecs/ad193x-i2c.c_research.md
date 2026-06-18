# sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-i2c.c

## Purpose
I2C bus glue for AD1936/AD1937 codecs. It configures the shared AD193x regmap for 8-bit I2C register and value fields and delegates component registration to the shared `ad193x_probe()`.

## Important APIs, Types, and Functions
`ad193x_id[]` maps `"ad1936"` and `"ad1937"` to `AD193X`. `ad193x_i2c_probe()` copies `ad193x_regmap_config`, sets `val_bits = 8` and `reg_bits = 8`, creates a devm I2C regmap, and calls `ad193x_probe()`.

## Control Flow
The module registers an `i2c_driver`. Probe performs no chip-specific initialization itself; all codec controls, DAI registration, and default writes happen in `ad193x.c`.

## State and Persistence
No local persistent state. The shared core stores private state on `client->dev`; the regmap owns register cache behavior as configured by the core and bus wrapper.

## Dependencies and Integration Points
Depends on Linux I2C, regmap, ASoC, and `ad193x.h`. It integrates AD1936/AD1937 I2C devices into the shared AD193x ASoC component.

## Risks
This wrapper passes `(uintptr_t)i2c_get_match_data(client)` as the type, but the driver table shown is an `i2c_device_id` table without an OF match table in this file; on legacy ID matching, match data availability should be checked against kernel API behavior. A wrong regmap width prevents all core register access.

## Test Signals
I2C probe with AD1936/AD1937 IDs, regmap bus transactions with 8-bit addresses, and successful shared-core control/DAI registration.
