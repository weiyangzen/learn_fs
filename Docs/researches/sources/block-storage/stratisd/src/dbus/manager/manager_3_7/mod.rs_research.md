# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_7/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r7` D-Bus interface.

Key behavior:
- Registers `ManagerR7` at the base path.
- Reuses r4 start-by-id behavior and r6 stop-by-id behavior.
- Reuses create/destroy/key/refresh/report behavior from earlier revisions.

Version-specific note:
- No new local methods are introduced in this file.
- It appears to preserve the r6 ABI under a new revision name.

Dependencies:
- `manager_3_4::start_pool_method`.
- `manager_3_6::stop_pool_method`.
- `manager_3_0` and `manager_3_2` helper functions.
