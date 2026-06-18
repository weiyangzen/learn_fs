# sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.h

## Purpose

`debugfs_netdev.h` declares the internal lifecycle interface for virtual-interface and link debugfs directories. It lets interface/link management code update debugfs state unconditionally while compiling to stubs when mac80211 debugfs support is disabled.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `ieee80211_debugfs_remove_netdev()`, `ieee80211_debugfs_rename_netdev()`, `ieee80211_debugfs_recreate_netdev()`, `ieee80211_link_debugfs_add()`, `ieee80211_link_debugfs_remove()`, `ieee80211_link_debugfs_drv_add()`, and `ieee80211_link_debugfs_drv_remove()`. Without debugfs, all are inline no-ops.

## Control Flow

No runtime control flow exists in the header. The Kconfig branch determines whether netdev/link lifecycle events manipulate debugfs or do nothing.

## State And Persistence

No state is stored here. The implementation stores dentry pointers in sdata/link structures and exposes runtime state only.

## Dependencies And Integration Points

It includes `ieee80211_i.h` for `struct ieee80211_sub_if_data` and `struct ieee80211_link_data`. `driver-ops.c` uses the driver add/remove declarations to refresh driver-owned debugfs during interface and MLO link changes. Interface creation/removal code uses the netdev functions.

## Risks

No-op stubs hide all debugfs lifecycle effects in non-debugfs builds, which is expected. Callers must not depend on debugfs side effects for correctness. The header keeps declarations separated from implementation details, so signature drift between header and implementation would be caught at build time.

## Test Signals

Build with debugfs enabled and disabled. Runtime checks in enabled builds should confirm dentry pointers are set/cleared on netdev and link lifecycle events and driver debugfs entries are refreshed across link changes.
