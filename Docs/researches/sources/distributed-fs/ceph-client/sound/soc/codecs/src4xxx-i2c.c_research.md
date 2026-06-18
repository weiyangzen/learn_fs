<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx-i2c.c

## Purpose
This is the I2C bus glue for the TI SRC4xxx/SRC4392 ASoC codec driver. It creates an I2C regmap and delegates all codec logic to the shared `src4xxx_probe()`.

## Important APIs, Types, And Functions
The central function is `src4xxx_i2c_probe()`, which calls `src4xxx_probe(&i2c->dev, devm_regmap_init_i2c(...), NULL)`. The file declares I2C ID `src4392`, OF compatible `ti,src4392`, and registers an `i2c_driver` named `src4xxx`.

## Control Flow
I2C core matches a device, probe initializes a devm regmap using `src4xxx_regmap_config`, and shared registration/configuration proceeds in `src4xxx.c`.

## State And Persistence
No private state is stored in this file. The shared driver stores state via `dev_set_drvdata()` after probe.

## Dependencies And Integration Points
It depends on Linux I2C, regmap, module device tables, and `src4xxx.h`. It is the transport-specific entry point for DT/I2C-described SRC4392 devices.

## Risks And Edge Cases
All probe errors are delegated through `src4xxx_probe()`. There is no explicit I2C match-data use, variant handling, or fallback if regmap creation fails beyond passing the error pointer to shared probe.

## Test Signals
I2C/DT binding, regmap creation failure handling, and successful shared component registration for a `ti,src4392` device cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx-i2c.c -->
