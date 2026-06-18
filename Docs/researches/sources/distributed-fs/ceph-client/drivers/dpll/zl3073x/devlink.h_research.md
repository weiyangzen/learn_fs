# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.h

## Purpose
This header declares the devlink-facing allocation, registration, and flash progress notification helpers for the ZL3073x core.

## Important APIs
`zl3073x_devm_alloc()` allocates the devlink instance and returns the embedded device state. `zl3073x_devlink_register()` registers the instance and parameters. `zl3073x_devlink_flash_notify()` wraps devlink flash progress notifications.

## Integration, state, risks, and tests
Transport probe uses allocation before initializing regmap. Core probe calls registration after DPLL setup. Flash and firmware code use the notification helper for user-visible progress. The header owns no state; build coverage catches prototype drift.
