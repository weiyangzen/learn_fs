# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/props.rs

Snapshot-origin and merge-scheduling helpers for filesystem r7+.

Key behavior:
- `origin_prop()` returns optional origin filesystem UUID as `(bool, uuid_string)`, using nil UUID when absent.
- `merge_scheduled_prop()` reads `fs.merge_scheduled()`.
- `set_merge_scheduled_prop()` calls `pool.set_fs_merge_scheduled` and maps `PropChangeAction` to changed/unchanged.
- `send_merge_scheduled_signal_on_change()` resolves the filesystem object path and emits the property signal.

This backs D-Bus control of snapshot merge scheduling.
