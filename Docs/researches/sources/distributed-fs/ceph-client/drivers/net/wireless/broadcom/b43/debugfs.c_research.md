# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.c

This file implements optional b43 debugfs support. It exposes per-device files for raw SHM/MMIO reads and masked writes, TX status logs, manual controller restart, LO calibration inspection, and dynamic debug feature toggles.

Lifecycle APIs are `b43_debugfs_init()`, `b43_debugfs_exit()`, `b43_debugfs_add_device()`, `b43_debugfs_remove_device()`, and `b43_debugfs_log_txstat()`. Generic `b43_debugfs_read()` and `b43_debugfs_write()` recover the `b43_wldev`, lock `wl->mutex`, reject devices below `B43_STAT_INITIALIZED`, allocate/copy buffers, and dispatch through per-file `b43_debugfs_fops`. File-specific handlers validate SHM routing/address or MMIO range/alignment, store the next read address, perform masked writes, print TX status circular logs, restart the controller when `restart` receives `1`, and dump G-PHY LO calibration data.

State lives in `struct b43_dfsentry`: per-file cached read buffers, next raw-access addresses, dynamic debug bools, and a `B43_NR_LOGGED_TXSTATUS` circular log. The state is runtime-only and removed with the debugfs subtree.

Dependencies include debugfs, file/user-copy APIs, b43 MMIO/SHM helpers, controller restart, TX status structures, LO calibration state, and `CONFIG_B43_DEBUG`. Risks are intentional raw hardware access from debugfs, semantic danger of writes despite range/alignment validation, 16 KiB per-read buffering, and cleanup ordering with device removal. Test signals include creation/removal of per-wiphy debugfs entries, invalid-address rejection, raw MMIO/SHM read/write behavior, TX status logging, restart trigger, LO output on G-PHY only, and no side effects when debug is disabled.
