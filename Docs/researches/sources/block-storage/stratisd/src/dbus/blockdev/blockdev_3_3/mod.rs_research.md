# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r3`.

Changes relative to r0-r2:
- Adds stored `connection` so property setters can emit change signals.
- Converts `UserInfo` from method-style mutation to a writable D-Bus property.
- Adds `NewPhysicalSize` property.
- Uses shared `set_blockdev_prop()` for setter flow: acquire mutable pool, apply change, emit signal only if changed.

Other properties remain inherited from r0 helpers.
