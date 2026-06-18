# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r4` D-Bus interface.

Key behavior:
- Registers `ManagerR4` at the Stratis base object path.
- Reexports and uses local `start_pool_method`.
- Reuses key, create/destroy, stop, refresh, version, and engine-report helpers from earlier manager revisions.

Version-specific note:
- Changes `start_pool` ABI from r3 by accepting `id: &str` and `id_type: &str`.
- `stop_pool` still uses an object path and delegates to `manager_3_2::stop_pool_method`.
- `create_pool` still includes ignored `redundancy`.

Dependencies:
- `manager_3_0`, `manager_3_2`, local `methods`.
- Engine types include `UnlockMethod`, `StoppedPoolsInfo`, `KeyDescription`.
