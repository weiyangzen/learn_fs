# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r7`.

Key behavior:
- Registers/unregisters `PoolR7`.
- Reuses r6 filesystem creation, r5 cache initialization, r3 grow, r1 properties, and r0 base methods.
- Adds `metadata(current)` and `filesystem_metadata(fs_name, current)` methods.

Version-specific addition:
- Read-only pool and filesystem metadata inspection becomes available over D-Bus.

Dependencies:
- `pool_3_7::{metadata_method, filesystem_metadata_method}`.
- `FilesystemSpec`.
