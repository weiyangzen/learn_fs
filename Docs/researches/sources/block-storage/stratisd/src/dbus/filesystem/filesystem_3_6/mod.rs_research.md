# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r6`.

Changes relative to r0-r5:
- Adds `SizeLimit` property.
- Adds writable setter for `SizeLimit` using shared `set_filesystem_prop()`.
- Emits size-limit change signal only when the value changes.
- Keeps `SetName` and base properties.

This revision introduces filesystem quota/limit control through D-Bus.
