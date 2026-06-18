# sources/distributed-fs/ceph-client/include/linux/backing-dev.h

## Purpose
Provides the public helper API for allocating, registering, querying, and using `backing_dev_info` and `bdi_writeback` objects from filesystems, block devices, and VM writeback paths.

## Important APIs, types, and functions
- Lifecycle: `bdi_alloc()`, `bdi_init()`, `bdi_register()`, `bdi_register_va()`, `bdi_unregister()`, `bdi_get_by_id()`, `bdi_get()`, and `bdi_put()`.
- Writeback control: `wb_start_background_writeback()`, `wb_workfn()`, `wb_wait_for_completion()`, `writeback_in_progress()`, and `wb_writeout_inc()`.
- Counters and policy: `wb_stat_mod()`, `wb_stat()`, `wb_stat_sum()`, `wb_stat_error()`, `bdi_get_min_bytes()`, `bdi_get_max_bytes()`, ratio/byte setters, and `bdi_set_strict_limit()`.
- Mapping helpers: `inode_to_bdi()`, `mapping_can_writeback()`, `inode_to_wb()`, `inode_to_wb_wbc()`, and unlocked inode-WB transaction helpers.
- Cgroup writeback helpers: `inode_cgwb_enabled()`, `wb_find_current()`, `wb_get_create_current()`, `wb_memcg_offline()`, and `wb_blkcg_offline()`.

## Control flow and state
Device setup allocates and registers a BDI, then filesystems use `inode_to_bdi()` and `inode_to_wb()` to attribute dirtying and writeback. For cgroup-aware filesystems, current task memory/io cgroups are mapped to a WB under RCU; missing or stale entries are created via `wb_get_create()`. Unlocked WB lookup uses `I_WB_SWITCH`, an RCU read-side section, and optional `i_pages` locking to keep inode-WB association stable.

## State and persistence behavior
The API manipulates in-memory BDI and WB lifetimes. `bdi_has_dirty_io()` uses aggregate write bandwidth as a dirtiness signal. Ratio and byte limit setters alter runtime dirty throttling policy. Cgroup writeback association can change dynamically with cgroup configuration and inode switching.

## Dependencies and integration points
Depends on scheduler, filesystem, device, writeback, slab, and `backing-dev-defs.h`. Integrated by address-space writeback checks, filesystem dirty accounting, cgroup writeback, blk-wbt, and global `bdi_wq`.

## Risks
Filesystems that support cgroup writeback must not use root-only helpers like `bdi_wb_dirty_exceeded()` and `bdi_wb_stat_mod()`. Calling unlocked inode-WB accessors while sleeping or without ending the transaction can leak RCU/locks. Incorrect BDI capabilities can either lose dirty accounting or throttle devices incorrectly.

## Test signals
Build both `CONFIG_CGROUP_WRITEBACK=y` and `n`. Exercise dirty accounting for normal and cgrouped writes, inode WB switching, BDI unregister while dirty work is pending, and strict dirty limit changes. Lockdep should not flag unlocked inode-WB lookup paths.
