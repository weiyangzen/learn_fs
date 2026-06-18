# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_8/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r8`.

Behavior:
- Carries forward r3+ writable-property API.
- Exposes `Devnode`, `HardwareInfo`, `UserInfo`, `InitializationTime`, `Pool`, `Uuid`, `Tier`, `PhysicalPath`, `TotalPhysicalSize`, and `NewPhysicalSize`.
- Uses r0 property helpers and r3 user-info/new-size helpers.

No additional behavior beyond revisioned compatibility.
