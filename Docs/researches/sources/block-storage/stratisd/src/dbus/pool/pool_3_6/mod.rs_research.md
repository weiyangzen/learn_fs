# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r6`.

Key behavior:
- Registers/unregisters `PoolR6`.
- Uses r6 `create_filesystems` with size-limit capable `FilesystemSpec`.
- Reuses r0 destroy/snapshot/add/rename/encryption methods.
- Uses r5 cache initialization.
- Reuses r1 properties and r3 grow method.

Version-specific addition:
- D-Bus create-filesystems signature changes from `Vec<(&str, (bool, &str))>` to `FilesystemSpec<'_>`.

Dependencies:
- `dbus::types::FilesystemSpec`.
- `pool_3_6::methods::create_filesystems_method`.
