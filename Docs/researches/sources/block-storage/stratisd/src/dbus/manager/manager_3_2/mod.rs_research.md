# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/mod.rs

D-Bus interface `org.storage.stratis3.Manager.r2`.

Changes relative to r0/r1:
- Replaces `LockedPools` exposure with `StoppedPools`.
- Adds `StartPool`.
- Adds `StopPool`.
- Adds `RefreshState`.
- Continues to expose key methods, create/destroy pool, version, and engine state report.

Important details:
- `StartPool` returns pool, blockdev, and filesystem object paths.
- `CreatePool` still delegates to r0 method and accepts unused redundancy.
- Registers at the D-Bus base path as another revisioned manager interface.
