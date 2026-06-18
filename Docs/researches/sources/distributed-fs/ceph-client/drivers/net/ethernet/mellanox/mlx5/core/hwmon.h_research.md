# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.h

## Purpose
`hwmon.h` declares the mlx5 hwmon registration interface and provides no-op stubs when hwmon support is not enabled.

## Important APIs, Types, And Functions
- With `CONFIG_HWMON`, it declares `mlx5_hwmon_dev_register`, `mlx5_hwmon_dev_unregister`, and `hwmon_get_sensor_name`.
- Without `CONFIG_HWMON`, registration returns success and unregister is an empty inline, allowing core code to call the API unconditionally.

## Control Flow And State
The header does not implement state. It defines a conditional lifecycle hook: register during device setup, unregister during teardown, and optionally query sensor names when hwmon state exists.

## Dependencies And Integration Points
It depends on `linux/mlx5/driver.h` and forward-declared mlx5 hwmon state from core headers. It integrates `hwmon.c` with core device initialization while keeping non-hwmon builds simple.

## Risks And Edge Cases
`hwmon_get_sensor_name` is only declared in hwmon-enabled builds; callers must be guarded accordingly. Stub registration returning 0 means higher-level code cannot use return value alone to know whether sensors exist.

## Test Signals
Build both `CONFIG_HWMON=y/m` and disabled configurations. Runtime signals are successful unconditional core calls and no unresolved symbols in non-hwmon builds.
