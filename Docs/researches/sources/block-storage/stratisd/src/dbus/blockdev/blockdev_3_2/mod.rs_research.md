# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_2/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r2`.

This revision matches r1/r0 behavior:
- Method-style `SetUserInfo`.
- Same read-only/read-write property surface as r0.
- Reuses r0 helper functions for property extraction and user-info mutation.
- Registers a separate revisioned zbus interface on the same object path.

No additional blockdev semantics are introduced in this file.
