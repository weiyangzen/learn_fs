# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r0`.

Key behavior:
- Defines `FilesystemR0` with engine, connection, manager, parent pool UUID, and filesystem UUID.
- Registers/unregisters this interface on a zbus object path.
- Exposes `SetName` method.
- Exposes properties:
  - `Created`
  - `Devnode`
  - `Name`
  - `Pool`
  - `Size`
  - `Used`
  - `Uuid`

Property reads use shared `filesystem_prop()` and r0 property helper functions.
