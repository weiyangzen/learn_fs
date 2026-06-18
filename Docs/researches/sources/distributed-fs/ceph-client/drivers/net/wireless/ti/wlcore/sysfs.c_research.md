# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.c

## Purpose
`sysfs.c` exposes a small sysfs control/status surface for wlcore devices: Bluetooth coexistence state, hardware PG version, and a binary firmware log stream.

## Important APIs, Types, and Functions
`bt_coex_state_show()` and `bt_coex_state_store()` back a read/write device attribute. Store parses a boolean, updates `wl->sg_enabled`, and if the chip is on resumes runtime PM and calls `wl1271_acx_sg_enable()`. `hw_pg_ver_show()` exposes `wl->hw_pg_ver` or `n/a`. `wl1271_sysfs_read_fwlog()` backs the binary `fwlog` attribute, consuming bytes from `wl->fwlog` and compacting the buffer. `wlcore_sysfs_init()` creates the two text attributes and binary file with cleanup on partial failure; `wlcore_sysfs_free()` removes them.

## Control Flow
Initialization is called after hardware registration in `main.c` probe completion. Attribute accesses lock `wl->mutex` around shared driver state. FW log reads may use interruptible locking and return zero once `wl->fwlog_size` is negative during teardown.

## State and Persistence Behavior
Sysfs state is live driver state only. `sg_enabled` persists only for the lifetime of `struct wl1271`; fwlog is a one-page in-memory FIFO-like buffer consumed destructively by reads. The `pos` argument is ignored because historical log data is not retained.

## Dependencies and Integration Points
Dependencies include Linux device attributes, binary sysfs attributes, runtime PM, `acx.h`, `wlcore.h`, `debug.h`, and `sysfs.h`. FW log data is produced by RX/logger and recovery paths in other files.

## Risks and Test Signals
Risks include returning `count` even on invalid store values, ignoring ACX return in bt coex store, fwlog readers racing with teardown, and destructive reads surprising tooling. Tests should create/remove sysfs files, toggle bt coexistence while off and on, read valid and `n/a` PG versions, read fwlog in partial chunks, and verify teardown unblocks readers.
