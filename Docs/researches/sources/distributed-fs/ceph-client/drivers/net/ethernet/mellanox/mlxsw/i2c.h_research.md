# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.h

## Purpose
`i2c.h` declares the optional mlxsw I2C bus-driver registration interface used by mlxsw device drivers that bind over I2C.

## Important APIs, Types, and Functions
- When `CONFIG_MLXSW_I2C` is enabled, it declares `mlxsw_i2c_driver_register()` and `mlxsw_i2c_driver_unregister()`.
- When disabled, inline stubs make registration fail with `-ENODEV` and unregistration a no-op.

## Control Flow
There is no internal control flow beyond compile-time `IS_ENABLED(CONFIG_MLXSW_I2C)` selection. Callers such as `minimal.c` can compile regardless of whether the I2C backend is enabled.

## State and Persistence
No runtime state exists in this header.

## Dependencies and Integration Points
It depends on `<linux/i2c.h>` and is consumed by mlxsw drivers that want the common I2C probe/remove implementation installed into their `struct i2c_driver`.

## Risks
The disabled stub returns `-ENODEV`, so module init code must unwind any earlier registration when I2C support is absent. Any future registration API change must keep enabled and disabled branches signature-compatible.

## Test Signals
Build with `CONFIG_MLXSW_I2C=y/m` and disabled. For disabled builds, module init should fail cleanly after unregistering any previously registered mlxsw core driver.
