# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.h

Purpose: Declares wl12xx debugfs initialization hook.

Important APIs and types: `wl12xx_debugfs_add_files(struct wl1271 *wl, struct dentry *rootdir)`.

Control flow: No control flow. The function is referenced by the wlcore ops table.

State and persistence: No state; implementation exposes volatile firmware stats through debugfs.

Dependencies and integration points: Included by `main.c` for `wl12xx_ops.debugfs_init` and by `debugfs.c`.

Risks: Signature must match wlcore's expected debugfs callback type.

Test signals: Build/link success and debugfs file creation after wlcore debugfs init.
