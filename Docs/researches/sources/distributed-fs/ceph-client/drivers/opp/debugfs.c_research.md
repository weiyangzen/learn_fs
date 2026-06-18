<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/opp/debugfs.c

## Purpose
`debugfs.c` exposes OPP tables, devices, OPP entries, clocks, supplies, and interconnect bandwidth values under `/sys/kernel/debug/opp`. It is observability infrastructure for the runtime OPP state maintained by `core.c`.

## Important APIs, Types, And Functions
The file keeps a single `rootdir`. OPP core calls `opp_debug_register()`, `opp_debug_unregister()`, `opp_debug_create_one()`, and `opp_debug_remove_one()`. Internal helpers create device names, per-clock rate files, per-supply voltage/current/power files, per-interconnect directories, and a `name` file backed by `bw_name_fops`.

## Control Flow
`opp_debug_init()` creates the root directory at `core_initcall` time. When a device is attached to an OPP table, `opp_debug_register()` creates the real directory for the first device or a symlink for later devices sharing the table. When an OPP is added, `opp_debug_create_one()` chooses a stable-ish directory name from rate and level for single-clock OPPs, otherwise from the current OPP count, then creates read-only files for availability, flags, level, latency, DT node name, clocks, supplies, and bandwidth.

Unregistering a device removes its symlink. If the removed device owns the real directory and the table is shared, `opp_migrate_dentry()` renames the directory to another device and removes that other device's old symlink.

## State And Persistence
Debugfs entries point directly at live fields inside `struct dev_pm_opp` and `struct opp_table`. The data persists only while the OPP/table exists and debugfs is mounted. The module stores `opp->dentry`, `opp_dev->dentry`, `opp_table->dentry`, and `opp_table->dentry_name` for cleanup/migration.

## Dependencies And Integration Points
This file depends on `CONFIG_DEBUG_FS`, debugfs primitives, device names, OF node names, interconnect path names, and OPP core lifecycle callbacks. Stub functions in `opp.h` remove this dependency when debugfs is disabled.

## Risks
Because files expose live object fields, lifetime ordering is critical. Debugfs removal must happen outside some locks to avoid circular dependencies, which is why OPP core defers certain `put` operations. The fallback directory name using `_get_opp_count()` can be unstable for non-rate/multi-clock tables. `opp_migrate_dentry()` uses `BUG_ON(!new_dev)` and assumes caller guarantees a shared table. Long device names are truncated by `NAME_MAX`.

## Test Signals
Validate debugfs creation for exclusive and shared OPP tables, symlink migration when the primary device is removed, OPP add/remove cleanup, multi-clock file names, regulator and interconnect files, concurrent table teardown under lockdep, and boot with debugfs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/debugfs.c -->
