# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r6` D-Bus interface.

Key behavior:
- Registers `ManagerR6` at the Stratis base path.
- Reuses r4 `start_pool_method`.
- Reexports local r6 `stop_pool_method`.
- Reuses create/destroy/key/report helpers from prior revisions.

Version-specific note:
- Changes `stop_pool` ABI to accept `id: &str` and `id_type: &str`.
- `create_pool` remains the r5-style version without redundancy.
- `stopped_pools` still uses `types::ManagerR2<StoppedPoolsInfo>`.

Dependencies:
- Local `methods.rs`.
- `manager_3_4::start_pool_method`.
- `manager_3_2::refresh_state_method` and `stopped_pools_prop`.
