# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/methods.rs

Purpose: Implements the base pool r0 method behavior reused by many later pool interfaces.

Major capabilities:
- Create filesystems, limited to one filesystem per call.
- Destroy filesystems and unregister their D-Bus objects.
- Snapshot a filesystem and register the snapshot object.
- Add data devices.
- Initialize cache and add cache devices.
- Rename pool.
- Bind, rebind, and unbind Clevis and keyring encryption metadata.

Common pattern:
- Looks up mutable pool guard from the engine by `PoolUuid`.
- Uses `tokio::task::spawn_blocking` for blocking engine/pool operations.
- Wraps engine actions with `handle_action!`.
- Converts results into D-Bus `(result, return_code, return_string)` tuples.
- Registers new blockdev/filesystem D-Bus objects after successful engine changes.
- Emits property change signals for affected pool/filesystem/blockdev properties.

Notable details:
- Filesystem sizes are accepted as strings and parsed into `u128` byte counts.
- Destroying filesystems emits origin update signals for affected origins.
- Rename emits pool name changes and filesystem devnode invalidation signals.
- Encryption bind/unbind operations track free token slot changes and emit keyring/Clevis/free-slot signals.
- r0 encryption methods use `OptionalTokenSlotInput::Legacy`.

Failure handling:
- Engine absence, parsing failures, join errors, and engine errors are converted to D-Bus error tuples.
