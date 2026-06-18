# sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.h

## Purpose

`debugfs_sta.h` declares station and link-station debugfs lifecycle helpers, with no-op stubs for non-debugfs builds. It lets station lifecycle and driver-operation code add/remove debugfs entries without direct Kconfig branching.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `ieee80211_sta_debugfs_add()`, `ieee80211_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_add()`, `ieee80211_link_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_drv_add()`, and `ieee80211_link_sta_debugfs_drv_remove()`. Without debugfs, all are inline empty functions.

## Control Flow

There is no runtime logic in the header. Compile-time Kconfig controls whether callers reach the implementation in `debugfs_sta.c`.

## State And Persistence

The header stores no state. The implementation stores debugfs dentries in station and link-station objects and exposes live runtime state only.

## Dependencies And Integration Points

It includes `sta_info.h` for `struct sta_info` and `struct link_sta_info`. `driver-ops.c` uses driver add/remove helpers during MLO station link changes. Station lifecycle code can call add/remove helpers unconditionally.

## Risks

The no-op stubs must remain behavior-free; callers must not require debugfs side effects for station correctness. Signature mismatches between header and implementation would be build-time failures.

## Test Signals

Build both debugfs and non-debugfs configurations. Enabled builds should create station/link debugfs entries and driver subentries; disabled builds should compile and run station lifecycle paths without debugfs references.
