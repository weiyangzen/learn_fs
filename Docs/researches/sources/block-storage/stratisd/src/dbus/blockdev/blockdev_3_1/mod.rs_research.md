# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_1/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r1`.

This revision is structurally the same as r0:
- Owns engine, manager, parent pool UUID, and blockdev UUID.
- Registers/unregisters `BlockdevR1`.
- Reuses r0 method/property helpers.
- Exposes method-style `SetUserInfo`.
- Exposes the same properties as r0.

Purpose is API revision continuity under a distinct interface name.
