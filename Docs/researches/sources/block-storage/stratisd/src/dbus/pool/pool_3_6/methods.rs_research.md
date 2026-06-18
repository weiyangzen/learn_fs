# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/methods.rs

Purpose: Implements r6 `create_filesystems_method`.

Key behavior:
- Accepts `FilesystemSpec`, whose entries include name, optional size, and optional size limit.
- Still rejects creation of more than one filesystem per call.
- Parses size and size-limit strings to `u128` and wraps them in `Bytes`.
- Calls `pool.create_filesystems` with `(name, size, size_limit)` tuples.
- Registers created filesystems on D-Bus.

Version-specific note:
- Adds filesystem size-limit support compared with r0.
- If filesystem D-Bus registration fails after engine creation, it logs a warning but continues returning success with whatever paths were registered.

Failure handling:
- Invalid size strings return D-Bus error status.
- Engine and task errors are converted through `engine_to_dbus_err_tuple`.
