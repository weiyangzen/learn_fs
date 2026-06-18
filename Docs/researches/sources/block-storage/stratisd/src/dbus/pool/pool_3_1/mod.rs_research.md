# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r1`.

Key behavior:
- Registers/unregisters `PoolR1` on per-pool object paths.
- Reuses r0 methods and properties.
- Adds r1 property support from local `props.rs`.

Version-specific additions:
- `fs_limit` readable/writable property.
- `overprovisioning` readable/writable property.
- `no_alloc_space` readable property.

Implementation note:
- Mutable properties use `set_pool_prop`, which obtains a write guard, applies the setter, and emits the corresponding signal on change.
