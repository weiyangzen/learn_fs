# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.h

Purpose: Declares wl1251 debugfs lifecycle functions.

Important APIs, types, and functions: `wl1251_debugfs_init`, `wl1251_debugfs_exit`, and `wl1251_debugfs_reset`.

Control flow: Called by wl1251 core probe/remove/reset paths to create, destroy, or clear debugfs-visible stats.

State and persistence: No direct state; implementation manages `wl->debugfs` and `wl->stats`.

Dependencies and integration points: Includes `wl1251.h`; implemented by `debugfs.c`.

Risks: Call order matters: reset assumes stats may already be allocated; exit assumes files were initialized.

Test signals: Build linkage and probe/remove/reset coverage with debugfs enabled and disabled.
