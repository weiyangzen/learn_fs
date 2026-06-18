# sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.h

## Purpose
Public interface for Greybus Bridged-PHY child drivers. It defines child-device and child-driver structures, registration helpers, and runtime-PM wrappers used by protocol drivers bound through the `gbphy` bus.

## Important APIs, Types, And Functions
`struct gbphy_device` stores ID, CPort descriptor, parent bundle, list node, and embedded `struct device`. `struct gbphy_device_id` matches by protocol ID. `struct gbphy_driver` provides name, probe/remove callbacks, ID table, and embedded `device_driver`. Macros include `GBPHY_PROTOCOL()`, `to_gbphy_dev()`, `to_gbphy_driver()`, and `module_gbphy_driver()`. PM wrappers are `gbphy_runtime_get_sync()`, `gbphy_runtime_put_autosuspend()`, `gbphy_runtime_get_noresume()`, and `gbphy_runtime_put_noidle()`.

## Control Flow
No standalone runtime flow. Child protocol modules declare a `gbphy_driver` and use `module_gbphy_driver()` to register it through `gb_gbphy_register_driver()`/`gb_gbphy_deregister_driver()`.

## State And Persistence
The header defines in-memory state only. Driver-private state is attached through `gb_gbphy_set_data()` and read by `gb_gbphy_get_data()`.

## Dependencies And Integration Points
Requires Greybus bundle/descriptor types from the including context and Linux device/runtime-PM APIs. Used by GPIO, I2C, PWM, and other bridged PHY protocol drivers.

## Risks
The PM wrappers compile to no-ops without `CONFIG_PM`, so drivers must not rely on them for non-PM synchronization. `gbphy_runtime_get_sync()` handles negative return by `pm_runtime_put_noidle()`; callers should not double-put on failure.

## Test Signals
Build both `CONFIG_PM=y` and `CONFIG_PM=n`. Exercise module registration macros, driver data helpers, PM wrapper failure paths, and protocol ID table matching through `gbphy.c`.
