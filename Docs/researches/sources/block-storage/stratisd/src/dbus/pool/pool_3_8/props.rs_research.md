# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/props.rs

This file provides D-Bus property adapter functions for pool interface revision 3.8 encryption metadata. Each function takes a read guard over a `Pool` and converts engine-level state into zbus-friendly values.

Key behavior:
- `free_token_slots_prop()` exposes `Pool::free_token_slots()` as the project’s tuple-as-option convention, defaulting to `0`.
- `metadata_version_prop()` casts the pool metadata version to `u64`.
- `volume_key_loaded_prop()` calls `Pool::volume_key_is_loaded(pool_uuid)` and returns either a boolean `Value` or an error string `Value`.
- `key_descs_prop()` handles both modern `EncryptionInfo` and legacy `PoolEncryptionInfo`:
  - modern info returns a vector of `(token_slot, key_description)`;
  - legacy info returns a tuple-option around the single key description;
  - unencrypted pools return string `"Unencrypted"`.
- `clevis_infos_prop()` mirrors key description handling, returning modern per-slot Clevis `(pin, json)` records, legacy single Clevis info, or `"Unencrypted"`.

Important dependencies:
- Uses `either::Either` because `Pool::encryption_info()` can expose modern or legacy encryption info.
- Uses `option_to_tuple()` from D-Bus utilities to preserve D-Bus ABI representation of optional values.
- Uses `zbus::zvariant::Value` where the concrete D-Bus payload type varies by encryption state/version.

Role in architecture:
- This is a compatibility adapter, not business logic. Token state and encryption information are owned by the engine; this file only normalizes it for r8 D-Bus clients.
