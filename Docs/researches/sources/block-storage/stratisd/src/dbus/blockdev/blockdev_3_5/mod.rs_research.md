# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_5/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r5`.

Behavior:
- Same as r4/r3: writable `UserInfo`, `NewPhysicalSize`, and inherited blockdev properties.
- Uses `set_blockdev_prop()` to emit user-info signals only on value changes.
- Separate interface revision for compatibility.

No file-local behavior change from r4.
