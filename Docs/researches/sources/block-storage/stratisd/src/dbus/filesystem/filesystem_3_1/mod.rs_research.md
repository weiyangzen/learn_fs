# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_1/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r1`.

Behavior:
- Same surface as r0: `SetName`, `Created`, `Devnode`, `Name`, `Pool`, `Size`, `Used`, `Uuid`.
- Reuses r0 methods and props.
- Registers as a separate revisioned interface on the filesystem object path.

No file-local semantic delta from r0.
