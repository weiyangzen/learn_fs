# sources/distributed-fs/ceph-client/net/mac80211/debugfs.h

## Purpose

`debugfs.h` is the small public-internal header for PHY-level mac80211 debugfs support. It lets the rest of mac80211 add hardware debugfs entries and use the common formatting helper when debugfs support is compiled in, while compiling to no-ops when it is disabled.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `debugfs_hw_add(struct ieee80211_local *local)` and `mac80211_format_buffer(char __user *userbuf, size_t count, loff_t *ppos, char *fmt, ...)` with `__printf(4, 5)` checking. Without debugfs, it provides an empty inline `debugfs_hw_add()` and does not expose the formatter.

## Control Flow

There is no runtime control flow in the header. Compile-time selection determines whether callers link to real debugfs code or no-op stubs.

## State And Persistence

No state is stored. The real implementation mutates debugfs dentries and runtime debug knobs in `debugfs.c`; this header only declares the interface.

## Dependencies And Integration Points

It includes `ieee80211_i.h` for `struct ieee80211_local`. `debugfs.c`, `debugfs_key.c`, and `debugfs_sta.c` depend on the formatter declaration when debugfs is enabled. mac80211 initialization code can call `debugfs_hw_add()` without surrounding its call in Kconfig conditionals.

## Risks

The fallback only stubs `debugfs_hw_add()`. Code that uses `mac80211_format_buffer()` must itself be compiled only under debugfs-enabled paths. A mismatch here would be a build failure rather than a runtime bug.

## Test Signals

Build both `CONFIG_MAC80211_DEBUGFS=y` and disabled configurations. The disabled build should have no unresolved references to `mac80211_format_buffer()`, and the enabled build should preserve printf-format checking for all formatter users.
