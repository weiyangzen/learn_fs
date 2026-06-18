# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r8`.

Key behavior:
- Registers/unregisters `PoolR8`.
- Reuses r6 filesystem creation, r5 cache initialization, r7 metadata methods, r3 grow, and r1 properties.
- Uses local r8 token-slot aware encryption methods.

Version-specific additions:
- Encryption methods accept optional token-slot parameters.
- Replaces older `key_description` and `clevis_info` properties with richer `key_descriptions` and `clevis_infos` zvariant values.
- Adds `free_token_slots`, `volume_key_loaded`, and `metadata_version` properties.
- `volume_key_loaded` emits no changed signal.
- `metadata_version` is const.

Dependencies:
- Local `methods.rs` and `props.rs`.
- `zbus::zvariant::Value` for richer property payloads.
