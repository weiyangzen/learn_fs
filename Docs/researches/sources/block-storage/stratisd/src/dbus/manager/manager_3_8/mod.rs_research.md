# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r8` D-Bus interface.

Key behavior:
- Registers `ManagerR8` at the base path.
- Exposes r8 `stopped_pools` wrapper type.
- Exposes r8 pool creation with multi-token encryption and integrity arguments.
- Exposes r8 pool start with optional key fd.
- Reuses r6 stop-by-id behavior.

Version-specific note:
- `stopped_pools` returns `types::ManagerR8<StoppedPoolsInfo>`, not `ManagerR2`.
- `create_pool` ABI now includes `journal_size`, `tag_spec`, and `allocate_superblock`.
- `start_pool` ABI now includes `key_fd`.

Dependencies:
- Local `methods.rs` and `props.rs`.
- Prior manager helpers for destroy/key/report/refresh/stop.
