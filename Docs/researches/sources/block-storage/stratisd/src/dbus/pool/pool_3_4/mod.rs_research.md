# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_4/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r4`.

Key behavior:
- Registers/unregisters `PoolR4`.
- Reuses r0 methods and properties.
- Reuses r1 filesystem-limit and overprovisioning properties.
- Reuses r3 physical-device growth method.

Version-specific note:
- No new local methods or properties are introduced.
- r4 preserves the r3 interface surface under a new revision name.
