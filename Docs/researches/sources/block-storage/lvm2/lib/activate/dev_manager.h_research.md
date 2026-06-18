# File Research: sources/block-storage/lvm2/lib/activate/dev_manager.h

## Role

`dev_manager.h` declares the private activation backend API used primarily by `activate.c` and segment-type target builders. It hides `struct dev_manager` while exposing construction, destruction, LV status, lifecycle, node, dependency, and utility functions.

## API Groups

- Lifecycle: `dev_manager_create()`, `dev_manager_destroy()`, `dev_manager_release()`, and `dev_manager_exit()`.
- Generic device info: `dev_manager_info()` returns DM info/read-ahead and optional segment status for an LV/layer.
- Target statuses: snapshot percent/status, mirror percent, RAID status/message, writecache message, cache status, thin status/device ID/pool status, VDO status and VDO size config.
- Lifecycle actions: `dev_manager_preload()`, `dev_manager_suspend()`, `dev_manager_activate()`, `dev_manager_deactivate()`, and `dev_manager_transient()`.
- Node and dependency helpers: `dev_manager_mknodes()`, `dev_manager_device_uses_vg()`, `dev_manager_check_prefix_dm_major_minor()`, and `dev_manager_get_dm_active_devices()`.
- Utility helpers: `read_only_lv()` and `get_crypt_table_offset()`.

## Dependency Context

The header includes `metadata-exported.h` and forward-declares most participating structs, keeping the interface lighter than the implementation. The API is still tightly coupled to LVM metadata concepts such as logical volumes, volume groups, LV segments, activation options, and target status objects.

## Important Invariants

- A `dev_manager` is scoped to a command context and VG name and uses an internal dm pool; many returned status objects refer to that pool.
- `track_pvmove_deps` at construction changes tree recursion behavior for pvmove operations.
- `dev_manager_suspend()` receives both lockfs and flush policy from `activate.c`; callers should not bypass the higher-level suspend logic unless they can supply those correctly.
