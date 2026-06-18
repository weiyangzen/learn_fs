# sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.h

## Purpose

`debugfs_key.h` declares the internal mac80211 key debugfs lifecycle API and provides no-op stubs for non-debugfs builds. It isolates key management code from direct Kconfig conditionals.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `ieee80211_debugfs_key_add()`, `ieee80211_debugfs_key_remove()`, `ieee80211_debugfs_key_update_default()`, `ieee80211_debugfs_key_remove_mgmt_default()`, and `ieee80211_debugfs_key_remove_beacon_default()`. Without debugfs, the same functions are inline empty stubs.

## Control Flow

There is no runtime logic in the header. Compile-time selection either wires key lifecycle events to real debugfs updates or drops them.

## State And Persistence

No state is held in the header. The real implementation stores dentry pointers in key and interface debugfs fields and reflects live key state only.

## Dependencies And Integration Points

The prototypes require `struct ieee80211_key` and `struct ieee80211_sub_if_data` to be visible to includers. Key installation/removal/default-key code can call these helpers unconditionally. The implementation depends on the `debugfs.c` PHY keys directory.

## Risks

The no-op stubs mean non-debugfs builds lose all key visibility, which is expected. Any caller that relies on side effects beyond diagnostics would be wrong. Type visibility must be maintained by includers because this header does not include all defining headers itself.

## Test Signals

Build with debugfs enabled and disabled. Enabled builds should update per-key directories and default symlinks; disabled builds should compile out all debugfs side effects with no behavior changes to key installation.
