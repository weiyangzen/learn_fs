# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_6/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r6`.

Behavior:
- Same blockdev property surface as r3-r5.
- Includes an explicit `#[allow(non_snake_case)]` on `devnode`, but the exposed property remains the same.
- Writable `UserInfo` and `NewPhysicalSize` are retained.
- Reuses r0/r3 helpers.

No storage semantic change is introduced here.
