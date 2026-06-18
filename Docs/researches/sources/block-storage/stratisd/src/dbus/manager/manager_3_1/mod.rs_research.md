# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_1/mod.rs

D-Bus interface `org.storage.stratis3.Manager.r1`.

Behavior:
- Same method/property surface as manager r0.
- Reuses r0 method and property implementations.
- Registers at the same base path as a separate revisioned interface.
- Keeps `LockedPools` property and `UnlockPool` method.

No file-local semantic delta from r0.
