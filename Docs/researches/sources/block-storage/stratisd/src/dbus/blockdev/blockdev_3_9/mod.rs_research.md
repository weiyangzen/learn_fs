# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_9/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r9`.

Behavior:
- Latest listed blockdev revision in this group.
- Same surface as r8/r7: writable `UserInfo`, `NewPhysicalSize`, and common blockdev properties.
- Uses manager lookups for pool path and change-signal routing.
- No unique semantic delta from r8 in this file.
