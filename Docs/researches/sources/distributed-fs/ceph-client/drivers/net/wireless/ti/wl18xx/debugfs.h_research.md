# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.h

## Purpose
Declares the wl18xx debugfs initialization hook.

## Important APIs, types, and functions
- `wl18xx_debugfs_add_files(struct wl1271 *wl, struct dentry *rootdir)` registers wl18xx debugfs files beneath the wlcore root.

## Control flow
No executable flow. The function is called through `wl18xx_ops.debugfs_init`.

## State and persistence behavior
No local state. The implementation creates runtime debugfs dentries and control callbacks.

## Dependencies and integration points
Uses `struct wl1271` and `struct dentry` from wlcore/Linux debugfs context. Integrated by `wl18xx/main.c`.

## Risks and test signals
Risk is prototype drift with the implementation or wlcore ops table. Build tests catch that; runtime test is presence of wl18xx debugfs directory and controls after device probe.
