# File Research: sources/block-storage/stratisd/src/dbus/util.rs

This large utility file centralizes D-Bus ABI helpers, error conversion, and property-change signal fan-out across all versioned Stratis D-Bus interfaces.

General conversion helpers:
- `tuple_to_option()` converts `(bool, T)` into `Option<T>`.
- `option_to_tuple()` converts `Option<T>` into `(bool, T)` with a default.
- `result_option_to_tuple()` encodes both result success/failure and optional value state into D-Bus variant-compatible form.
- `engine_to_dbus_err_tuple()` maps `StratisError` into `(ERROR, description)`, unwrapping core device-mapper errors for clearer messages.

Signal infrastructure:
- Internal `send_signal!` macro:
  - retrieves a typed interface from the zbus object server;
  - calls the generated property change/invalidation signal method;
  - logs warning on lookup or send failure.
- The rest of the file is mostly explicit fan-out helpers that emit one logical property change to every D-Bus interface revision that exposes that property.

Pool signal helpers:
- `send_pool_background_signals()`:
  - uses pool diffs to emit allocated size, used size, and no allocation space changes for background event handling.
- `send_pool_foreground_signals()`:
  - emits allocated size, used size, total physical size, and no allocation space changes for foreground operations.
- Specific helpers fan out:
  - pool name changes, also invalidating filesystem devnodes;
  - overprovisioning;
  - filesystem limit;
  - Clevis info;
  - keyring/key descriptions;
  - free token slots;
  - action availability;
  - cache presence;
  - encrypted status, r9 only;
  - last reencryption timestamp, r9 only.

Filesystem signal helpers:
- Background filesystem diffs emit size and used changes.
- Dedicated helpers emit size, used, origin, size limit, merge scheduled, and name/devnode invalidation signals across the revisions that expose each property.

Manager signal helpers:
- `send_locked_pools_signals()` emits on manager r0 and r1.
- `send_stopped_pools_signals()` emits on manager r2 through r9.

Blockdev signal helpers:
- Emit new physical size, user info, and total physical size across appropriate blockdev revisions.

Compatibility behavior:
- Older pool r0-r7 clients see singular `key_description`/`clevis_info` signals only when the changed token is the lowest/legacy slot.
- r8/r9 clients always receive plural `key_descriptions`/`clevis_infos` signals.
- r9-only additions are deliberately not fanned out to older revisions.

Role in architecture:
- This file is the D-Bus notification backbone. It keeps the versioned ABI consistent by making every state-changing path call one shared signal helper instead of duplicating revision fan-out logic.
