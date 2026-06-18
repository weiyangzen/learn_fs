# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/mod.rs

This file defines the `PoolR9` zbus interface implementation for `org.storage.stratis3.pool.r9`.

Structure:
- Holds shared service state:
  - `Arc<Connection>`
  - `Arc<dyn Engine>`
  - `Lockable<Arc<RwLock<Manager>>>`
  - object path counter
  - pool UUID
- Provides `new()`, `register()`, and `unregister()` helpers for object-server registration.
- Declares `methods` and `props` submodules.
- Re-exports r9 methods and `last_reencrypted_timestamp_prop`.

Interface composition:
- Most methods/properties are imported from earlier pool interface versions:
  - r0: core pool operations/properties such as create/destroy filesystems, add devices, name, size, used, encrypted.
  - r1: filesystem limit, overprovisioning, no allocation space.
  - r3: grow physical device.
  - r5: init cache.
  - r6: create filesystems.
  - r7: metadata and filesystem metadata.
  - r8: keyring/Clevis bind/rebind/unbind and token metadata.
- r9 adds:
  - `encrypt_pool`
  - `reencrypt_pool`
  - `decrypt_pool`
  - `last_reencrypted_timestamp`

D-Bus methods:
- Exposes filesystem creation/destruction/snapshot, device addition/cache init, naming, encryption token management, physical growth, metadata fetch, and r9 pool encryption lifecycle methods.
- Each method delegates to a free function with the shared engine/connection/manager/counter/UUID context.

D-Bus properties:
- `uuid` is const.
- Mutable/signaled pool properties include `name`, `encrypted`, `available_actions`, key descriptions, Clevis infos, cache state, physical sizes, allocation, filesystem limit, overprovisioning, no allocation space, free token slots, and last reencryption timestamp.
- `volume_key_loaded` uses `emits_changed_signal = "false"`.
- `metadata_version` is const.
- Setters for `fs_limit` and `overprovisioning` use `set_pool_prop()` with signal-on-change callbacks.

Role in architecture:
- This file is the versioned D-Bus facade for pool revision r9. It preserves backward-compatible behavior by reusing older revision implementations while adding online encryption/decryption operations and last reencryption timestamp visibility.
