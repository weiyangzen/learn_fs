# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r3`.

Key behavior:
- Registers/unregisters `PoolR3`.
- Reuses r0 pool lifecycle/encryption methods.
- Reuses r1 properties.
- Adds `grow_physical_device(dev)` using local r3 method implementation.

Version-specific addition:
- Public D-Bus method for growing a physical device by device UUID string.

Dependencies:
- `pool_3_3::methods::grow_physical_device_method`.
- r0 and r1 helper functions.
