# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_2/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r2`.

Key behavior:
- Registers/unregisters `PoolR2`.
- Reuses r0 methods and r1 mutable property behavior.
- Exposes the same method/property set as r1 in this file.

Version-specific note:
- No local methods or props are introduced.
- This is a compatibility revision wrapper over r1 behavior.

Dependencies:
- r0 method/property helpers.
- r1 property and setter helpers.
- Shared `pool_prop` and `set_pool_prop`.
