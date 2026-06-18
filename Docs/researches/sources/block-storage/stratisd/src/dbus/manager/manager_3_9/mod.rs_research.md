# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r9` D-Bus interface.

Key behavior:
- Registers `ManagerR9` at the base path.
- Reuses r8 create-pool and stopped-pools behavior.
- Reuses r6 stop-by-id behavior.
- Adds r9 `start_pool` signature with `remove_cache`.

Version-specific note:
- `start_pool` arguments are `id`, `id_type`, `unlock_method`, `key_fd`, and `remove_cache`.
- Other methods remain aligned with r8.

Dependencies:
- `manager_3_8::{create_pool_method, stopped_pools_prop}`.
- Local `methods::start_pool_method`.
- Prior manager helpers for key, destroy, refresh, report, and stop.
