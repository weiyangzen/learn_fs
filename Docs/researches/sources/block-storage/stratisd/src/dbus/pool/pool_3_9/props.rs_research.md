# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/props.rs

This file contains the r9-specific pool property adapter:
- `last_reencrypted_timestamp_prop()`

Behavior:
- Reads `Pool::last_reencrypt()` from a pool read guard.
- Converts `Option<DateTime<Utc>>` into D-Bus tuple-as-option form.
- Formats timestamps as RFC3339 with seconds precision and UTC `Z` formatting via `chrono::SecondsFormat::Secs`.
- Uses an empty string as the default value when no reencryption timestamp exists.

Role in architecture:
- This is the D-Bus representation layer for the r9 `last_reencrypted_timestamp` property. The timestamp is produced by engine/pool finalization logic; this file only formats it.
