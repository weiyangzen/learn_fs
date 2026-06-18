# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/props.rs

Size-limit property helpers for filesystem r6+.

Key behavior:
- `size_limit_prop()` returns optional size limit bytes as `(bool, String)`.
- `set_size_limit_prop()` parses optional string into `devicemapper::Bytes` and calls `pool.set_fs_size_limit`.
- Maps `PropChangeAction::NewValue` to changed, `Identity` to unchanged.
- `send_size_limit_signal_on_change()` resolves filesystem object path from manager and sends D-Bus signal.

This is the mutation backend for the r6 `SizeLimit` property.
