# sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_i2c.c

## Purpose
I2C transport driver for FXAS21002C.

## Important APIs, Types, And Functions
Defines 8-bit I2C regmap config, `fxas21002c_i2c_probe`, `fxas21002c_i2c_remove`, I2C/OF match tables, and an `i2c_driver` importing `IIO_FXAS21002C`.

## Control Flow
Probe initializes regmap over I2C and delegates to `fxas21002c_core_probe` with IRQ and device name. Remove delegates to core remove.

## State And Persistence
No local runtime state beyond the devm regmap and driver binding.

## Dependencies And Integration Points
Depends on I2C, REGMAP_I2C, shared PM ops, `nxp,fxas21002c` compatible, and core namespace exports.

## Risks
Regmap config is minimal and assumes default I2C register semantics. The probe passes `i2c->name`, so naming must match userspace expectations and core channel naming.

## Test Signals
Build/probe via I2C ID and OF compatible, verify regmap init failures, IRQ forwarding, PM ops, and core sysfs behavior.
