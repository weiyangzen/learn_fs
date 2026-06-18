# sources/distributed-fs/ceph-client/sound/soc/codecs/adav803.c

## Purpose
I2C bus wrapper for the ADAV803 codec using shared ADAV80x logic.

## APIs, Types, and Functions
Defines I2C ID `adav803`, `adav803_probe()`, and an `i2c_driver`. Probe initializes an I2C regmap using `adav80x_regmap_config` and calls `adav80x_bus_probe()`.

## Control Flow, State, and Persistence
All state is owned by `adav80x.c`; this file only adapts I2C transport to the common component.

## Dependencies and Integration
Depends on I2C, regmap, ASoC, and `adav80x.h`. It binds by I2C modalias rather than an OF table in this source.

## Risks and Test Signals
Risks are minimal but include no OF match table and any mismatch between the shared regmap pad/register layout and I2C bus framing. Test signals are I2C probe, regmap access, and shared component registration with two audio interfaces.
