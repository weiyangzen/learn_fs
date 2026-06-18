# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/mod.rs

Purpose: Defines the `org.storage.stratis3.pool.r0` D-Bus interface.

Key behavior:
- Registers/unregisters `PoolR0` instances at per-pool object paths.
- Stores connection, engine, manager registry, object-path counter, and pool UUID.
- Exposes r0 pool methods from local `methods.rs`.

Exposed methods:
- Filesystem create/destroy/snapshot.
- Data/cache device add and cache initialization.
- Pool rename.
- Clevis/keyring bind, rebind, and unbind.

Exposed properties:
- `uuid`, `name`, `encrypted`, `available_actions`.
- `key_description`, `clevis_info`, `has_cache`.
- `total_physical_size`, `total_physical_used`, `allocated_size`.

Implementation note:
- Property getters use shared `pool_prop` to fetch a read guard and map missing pools to D-Bus errors.
