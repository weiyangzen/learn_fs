# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-i2c.c

## Purpose
I2C bus wrapper for ADAU1361/ADAU1461/ADAU1761/ADAU1961 codec core. It configures bus-specific regmap widths and delegates probe/remove to the shared ADAU1761/ADAU17x1 implementation.

## Important APIs, Types, and Functions
`adau1761_i2c_probe()` copies `adau1761_regmap_config`, sets `val_bits = 8` and `reg_bits = 16`, creates an I2C regmap, and calls `adau1761_probe()` with the matched variant ID and no switch-mode callback. `adau1761_i2c_remove()` calls `adau17x1_remove()`. ID and OF tables cover ADAU1361, ADAU1461, ADAU1761, and ADAU1961.

## Control Flow
I2C probe performs bus setup then delegates all codec registration and initialization to the core. Remove delegates shared cleanup.

## State and Persistence
No local persistent state. Shared core stores device state and regmap cache.

## Dependencies and Integration Points
Depends on I2C, regmap, ASoC, and `adau1761.h` from the same codec family. Integrates through legacy IDs and OF compatible strings.

## Risks
Variant IDs must remain aligned with the shared core's enum. If OF match data is not supplied, this code relies on the I2C ID table path for variant data.

## Test Signals
Probe/remove for each ID, OF matching, regmap transaction width validation, and shared-core controls/DAI operation.
