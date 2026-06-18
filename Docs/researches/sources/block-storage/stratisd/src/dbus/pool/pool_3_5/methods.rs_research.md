# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/methods.rs

Purpose: Implements r5 `init_cache_method`.

Key behavior:
- Looks up mutable pool by UUID.
- Converts supplied `PathBuf` devices to borrowed paths.
- Calls `pool.init_cache(pool_uuid, name, devices, true)`.
- Emits has-cache signal on successful cache initialization.
- Registers new cache blockdev objects and returns their paths.

Version-specific note:
- Differs from r0 `init_cache_method`, which calls `pool.init_cache(..., false)`.
- This revision changes engine behavior while keeping the D-Bus method result shape.

Failure handling:
- Missing pool, engine errors, and task join errors become D-Bus error tuples.
