# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_5/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r5` D-Bus interface.

Key behavior:
- Registers `ManagerR5` at the base path.
- Preserves r4 `start_pool` id/id_type behavior by importing `manager_3_4::start_pool_method`.
- Reuses stop/refresh/stopped-pools behavior from `manager_3_2`.
- Reuses key and report methods from `manager_3_0`.

Version-specific note:
- Removes the unused `redundancy` argument from `create_pool`.
- Otherwise closely mirrors r4.

Dependencies:
- `zbus` interface generation and object-path types.
- Shared `Manager` registry and `Engine` trait.
