# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_3/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r3` D-Bus interface implementation.

Key behavior:
- Registers `ManagerR3` at `consts::STRATIS_BASE_PATH`.
- Stores shared `Connection`, `Engine`, `Manager` path registry, and object-path counter.
- Exposes manager version, stopped pools, key management, pool creation/destruction, pool start/stop, refresh, and engine-state reporting.
- Reuses most behavior from `manager_3_0` and `manager_3_2`.

Version-specific note:
- `create_pool` still accepts a `redundancy: (bool, u16)` argument but ignores it.
- `start_pool` accepts only `pool_uuid: &str`, not a generic id/id_type pair.

Dependencies:
- `zbus::interface`, `Fd`, `ObjectPath`, `OwnedObjectPath`.
- Engine types: `Engine`, `KeyDescription`, `StoppedPoolsInfo`, `UnlockMethod`.
