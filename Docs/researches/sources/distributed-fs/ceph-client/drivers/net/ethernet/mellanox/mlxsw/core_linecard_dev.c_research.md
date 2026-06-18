# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecard_dev.c

## Purpose
`core_linecard_dev.c` turns each provisioned mlxsw line card into an auxiliary bus device and attaches a nested devlink instance to it. This gives a line card its own devlink information and firmware flashing surface while the parent line-card manager owns provisioning and state transitions.

## Important APIs, Types, and Functions
- `struct mlxsw_linecard_bdev` embeds `struct auxiliary_device`, points at the owning `struct mlxsw_linecard`, and stores the allocated nested devlink private object.
- A global `IDA` allocates stable auxiliary device IDs. `mlxsw_linecard_bdev_release()` frees the ID and object after auxiliary-device lifetime ends.
- `mlxsw_linecard_bdev_add()` / `mlxsw_linecard_bdev_del()` are called by `core_linecards.c` when provisioning is set or cleared.
- `mlxsw_linecard_bdev_probe()` allocates a devlink with `mlxsw_linecard_dev_devlink_ops`, links it to the parent devlink linecard through `devlink_linecard_nested_dl_set()`, and registers it. Remove unregisters and frees that devlink.
- `mlxsw_linecard_driver_register()` / `mlxsw_linecard_driver_unregister()` wrap `auxiliary_driver_register()` and `auxiliary_driver_unregister()`.

## Control Flow
Provisioning allocates an ID, allocates and initializes an auxiliary device named `lc`, sets the parent to the mlxsw bus device, then adds it to the auxiliary bus. The auxiliary driver probe creates a nested devlink. Devlink `info_get` delegates to `mlxsw_linecard_devlink_info_get()`, while `flash_update` delegates to `mlxsw_linecard_flash_update()`. Unprovisioning deletes and uninitializes the auxiliary device; the release callback completes memory and ID cleanup.

## State and Persistence
The file persists only kernel object lifetime state: auxiliary ID allocation, parent/child device references, `linecard->bdev`, and the nested devlink private pointer. Firmware state and line-card readiness live in `core_linecards.c` and hardware.

## Dependencies and Integration Points
It depends on the auxiliary bus, devlink, IDA, and the line-card APIs exported by `core_linecards.c`. It is the bridge between devlink's nested line-card model and mlxsw's internal line-card object.

## Risks
The nested devlink is only valid after probe completes; call sites must tolerate line cards that are provisioned but whose auxiliary probe failed. `mlxsw_linecard_bdev_del()` must be idempotent because unprovisioned cards do not have `bdev`. Lifetime correctness depends on using auxiliary device delete/uninit rather than freeing directly.

## Test Signals
Provision/unprovision a line card and verify auxiliary device creation/removal, nested devlink visibility, `devlink dev info` output, and line-card `devlink flash` delegation. Error-path tests should cover ID allocation failure, `auxiliary_device_init()` failure, `auxiliary_device_add()` failure, and `devlink_linecard_nested_dl_set()` failure.
