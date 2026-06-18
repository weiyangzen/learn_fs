# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/methods.rs

Purpose: Implements r3 `grow_physical_device_method`.

Key behavior:
- Parses block device UUID from string.
- Looks up mutable pool by UUID.
- Calls `pool.grow_physical(&name, pool_uuid, dev)`.
- Runs the engine action through `handle_action!`.
- Sends pool foreground diff signals when a diff is returned.
- Emits blockdev physical-size signal for the grown device.

Return semantics:
- Changed action returns `(true, OK, OK_STRING)`.
- Identity/no-change returns `(false, OK, OK_STRING)`.
- Parse, engine, and task errors are converted to D-Bus error tuples.
