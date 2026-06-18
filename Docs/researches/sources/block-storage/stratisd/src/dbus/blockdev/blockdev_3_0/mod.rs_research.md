# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/mod.rs

D-Bus interface implementation `org.storage.stratis3.blockdev.r0`.

Key behavior:
- Defines `BlockdevR0` with engine, manager, parent pool UUID, and blockdev UUID.
- Registers/unregisters the object with zbus object server.
- Exposes method `SetUserInfo`.
- Exposes properties:
  - `Devnode`
  - `HardwareInfo`
  - `UserInfo`
  - `InitializationTime`
  - `Pool`
  - `Uuid`
  - `Tier`
  - `PhysicalPath`
  - `TotalPhysicalSize`

Property reads are delegated to shared `blockdev_prop()` plus r0 property functions.
