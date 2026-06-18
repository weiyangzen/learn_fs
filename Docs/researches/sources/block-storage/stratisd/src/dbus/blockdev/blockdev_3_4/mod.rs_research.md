# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_4/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r4`.

Behavior:
- Same r3 property-style API.
- Keeps writable `UserInfo`.
- Keeps `NewPhysicalSize`.
- Reuses r0 common property helpers and r3 setter/signal helpers.
- Registers as a distinct revisioned interface.

No unique semantic delta from r3 is present in this file.
