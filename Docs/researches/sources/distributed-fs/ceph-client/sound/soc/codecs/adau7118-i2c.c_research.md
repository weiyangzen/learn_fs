# sources/distributed-fs/ceph-client/sound/soc/codecs/adau7118-i2c.c

## Purpose
I2C wrapper and regmap description for software-controlled ADAU7118 PDM-to-I2S/TDM converters.

## APIs, Types, and Functions
Defines `adau7118_reg_defaults` for vendor/device/revision, enables, decimation/clock-map, HPF, serial-port controls, eight channel slot registers, drive strength, and reset. `adau7118_volatile()` marks the reset register volatile. `adau7118_probe_i2c()` creates an 8-bit I2C regmap and calls `adau7118_probe(..., false)`. OF and I2C ID tables register the `adau7118` I2C driver.

## Control Flow, State, and Persistence
Probe initializes regmap and transfers all persistent behavior to `adau7118.c`. Regcache defaults are used while the core driver powers regulators off and sets cache-only mode.

## Dependencies and Integration
Depends on I2C, regmap, and the common header register definitions. Integrates with OF compatible `adi,adau7118`.

## Risks and Test Signals
Risks include reset register volatility, shared compatible string with hardware-mode platform wrapper, and default slot map correctness for board channel order. Test signals are successful I2C regmap init, soft reset in common probe, device-property decimation/clock-map programming, and regcache sync after regulator power-up.
