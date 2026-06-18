# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_import.c

## Scope

Provides libzfs import-support callbacks, label clearing, and device-in-use detection for pool/vdev labels.

## APIs And Behavior

- `libzfs_config_ops` supplies `refresh_config_libzfs()` and `pool_active_libzfs()` to the shared import logic.
- `refresh_config()` sends a trial config through `ZFS_IOC_POOL_TRYIMPORT`, growing the destination nvlist on `ENOMEM`.
- `pool_active()` opens a pool silently and compares the active pool GUID against the label/config GUID.
- `zpool_clear_label()` scans all vdev labels, validates GUID and pool state, zeros the label nvlist/uberblock area while leaving leading pad space intact, and also clears an L2ARC header when the label indicates an L2 cache device.
- `zpool_in_use()` reads a vdev label and decides whether the device is active, exported, potentially active, spare, L2ARC, or unused. It checks active configs by GUID, searches aux spares/cache devices across imported pools, and returns the pool name/state when in use.

## State And Dependencies

The file depends on vdev labels, pool config nvlists, import ioctls, zpool iteration/open helpers, `zpool_read_label()`, `fstat64_blk()`, and libzutil label/config constants.

## Risks And Invariants

Device in-use results are conservative around active/exported labels and shared spares. Label clearing only succeeds if at least one valid label was overwritten and, for L2ARC labels, the header was also cleared. Active-pool checks rely on matching GUIDs rather than names alone.
