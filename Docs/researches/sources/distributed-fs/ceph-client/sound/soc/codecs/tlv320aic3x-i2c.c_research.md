# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic3x-i2c.c

## Purpose
Provides the I2C wrapper for the TLV320AIC3x family shared codec driver.

## Important APIs, Types, and Functions
`aic3x_i2c_probe()` configures `aic3x_regmap` for 8-bit register/value I2C access, initializes regmap, and calls `aic3x_probe()` with match data. `aic3x_i2c_remove()` calls `aic3x_remove()`. ID tables cover AIC3x, AIC33, AIC3007, AIC3104, and AIC3106 model constants.

## Control Flow
The I2C module registers with `module_i2c_driver()`. Probe is a thin transport setup path; all regulator, reset, control, DAI, and DAPM behavior is in `tlv320aic3x.c`.

## State and Persistence
The wrapper stores no private state. The shared core attaches `struct aic3x_priv` to the device and owns all persistent model, clock, power, GPIO, and control state.

## Dependencies and Integration Points
Depends on I2C, regmap, OF matching, and ASoC. Integrates through exported `aic3x_regmap`, `aic3x_probe()`, and `aic3x_remove()`.

## Risks
OF compatible entries do not carry `.data`, so OF-only instantiation depends on I2C ID matching or bus-provided match data for nonzero model selection. Regmap errors are deferred to the common probe via `IS_ERR()`.

## Test Signals
Probe all I2C IDs, verify correct model-specific controls/widgets appear, test OF boot paths for model data selection, and inject missing supplies/reset GPIO behavior through the shared core.
