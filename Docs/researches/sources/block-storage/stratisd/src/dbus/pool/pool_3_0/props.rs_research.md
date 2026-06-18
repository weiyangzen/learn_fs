# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/props.rs

Purpose: Implements r0 pool property adapters.

Properties:
- `name_prop`: extracts engine pool name.
- `size_prop`: total physical size as decimal string.
- `used_prop`: optional total used as `(bool, String)`.
- `allocated_prop`: allocated size as decimal string.
- `encrypted_prop`: encryption status.
- `avail_actions_property`: available action flags.
- `key_description_property`: legacy and newer encryption key description shape.
- `clevis_info_property`: legacy and newer Clevis info shape.
- `has_cache_property`: cache presence.

Important detail:
- Handles both legacy encryption info and newer per-token encryption info through `Either`.
- Uses D-Bus option encoding helpers to represent optional nested values.
