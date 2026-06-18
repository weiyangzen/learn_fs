# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.h

## Purpose
`sysfs.h` declares the sysfs lifecycle hooks for wlcore.

## Important APIs
It declares `wlcore_sysfs_init(struct wl1271 *wl)` and `wlcore_sysfs_free(struct wl1271 *wl)`. The header relies on callers already having a visible `struct wl1271` declaration through surrounding includes.

## Control Flow, State, and Integration
No logic or state exists in the header. `main.c` calls init after registering mac80211 hardware and calls free from `wlcore_free_hw()`. The header keeps sysfs implementation details out of the core file.

## Risks and Test Signals
Risks are limited to lifecycle mismatch: every successful init must be paired with free, and callers need appropriate include ordering for `struct wl1271`. Compile coverage plus probe/remove sysfs tests validate it.
