# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r5`.

Key behavior:
- Registers/unregisters `PoolR5`.
- Reuses most r0 methods.
- Uses local r5 `init_cache_method`.
- Reuses r1 properties and r3 physical growth.

Version-specific addition:
- `init_cache` now delegates to the r5 implementation, which passes `true` to the engine cache initialization call.

Dependencies:
- `pool_3_5::methods::init_cache_method`.
- r0/r1/r3 helper functions.
