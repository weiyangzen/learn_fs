# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.c

Purpose: Exposes wl1251 firmware and driver statistics through debugfs and manages the debugfs lifecycle.

Important APIs, types, and functions: Public APIs are `wl1251_debugfs_init()`, `wl1251_debugfs_exit()`, and `wl1251_debugfs_reset()`. Macro-generated file operations expose fields from `struct acx_statistics`; custom readers expose TX queue length/status and retry counters. `wl1251_debugfs_update_stats()` refreshes firmware statistics with a 1000 ms cache lifetime.

Control flow: Init allocates `wl->stats.fw_stats`, creates root and `fw-statistics` dirs, seeds update timestamp, and creates many read-only files. Reads of firmware-stat files wake ELP, conditionally interrogate `ACX_STATISTICS`, let firmware sleep, then format one counter. Exit removes every file and directory and frees stats memory. Reset zeros cached firmware stats and driver counters.

State and persistence: Maintains in-memory cached stats and debugfs dentries under `wl->debugfs`. Debugfs files are runtime-only and disappear on module/device removal.

Dependencies and integration points: Depends on debugfs, simple file operations, wl1251 mutex, ELP power-save helpers, ACX statistics interrogation, skb queue state, and `KBUILD_MODNAME` for root directory.

Risks: `debugfs_create_*` return values are not checked; later remove calls tolerate NULL but missing files may go unnoticed. Stats reads take `wl->mutex` and may wake firmware, so debugfs access can affect power behavior. The file list is manually mirrored in add/delete macros and can drift.

Test signals: Mount debugfs and read all files while device is on/off/ELP, verify no leaks on init failure/removal, confirm stats cache throttling, and check queue status reflects stopped/running TX queue.
