# sources/distributed-fs/ceph-client/include/linux/backing-dev-defs.h

## Purpose
Defines the core backing-device and writeback data structures used by the VM, filesystem, and block layers to track dirty data, writeback bandwidth, throttling, and cgroup-specific writeback ownership.

## Important APIs, types, and functions
- `enum wb_state`, `enum wb_stat_item`, and `enum wb_reason` describe writeback state bits, per-wb counters, and trigger reasons.
- `struct wb_completion` and `WB_COMPLETION_INIT` support waiting for queued writeback work.
- `struct bdi_writeback` owns dirty inode lists, writeback work queues, bandwidth estimates, throttling fields, and optional memcg/blkcg associations.
- `struct backing_dev_info` owns device-level identity, readahead/IO limits, reference count, capabilities, aggregate bandwidth, root `bdi_writeback`, cgroup-wb index, waitqueue, and debug/device metadata.
- Inline refcount helpers `wb_tryget()`, `wb_get()`, `wb_put_many()`, `wb_put()`, and `wb_dying()` abstract cgroup versus root writeback lifetime rules.

## Control flow and state
Callers register a `backing_dev_info`, then writeback code queues work onto a `bdi_writeback` and moves inodes among `b_dirty`, `b_io`, `b_more_io`, and `b_dirty_time` under `list_lock`. Work scheduling is guarded by `work_lock`. With cgroup writeback, per-memcg/blkcg writeback objects are indexed through `cgwb_tree` and refcounted independently.

## State and persistence behavior
All state is in-memory kernel state. Dirty counters are percpu and approximate until summed. Write bandwidth and throttle rates persist for the lifetime of the BDI/WB and inform later dirty throttling. Cgroup writeback objects pin associated cgroup CSS objects and are released asynchronously via percpu refs, work, or RCU.

## Dependencies and integration points
Depends on kernel list, radix-tree, rb-tree, spinlock, percpu counter/refcount, flex proportions, workqueue, timer, kref, and refcount APIs. Integrated by `backing-dev.h`, writeback core, filesystems, memory cgroups, block cgroups, debugfs, and device model ownership.

## Risks
Locking and lifetime are the primary hazards. Dirty inode lists require `list_lock`; work queues require `work_lock`; cgroup writeback requires percpu-ref and RCU discipline. `WB_has_dirty_io` and `tot_write_bandwidth` are used as fast signals and can become misleading if not updated consistently.

## Test signals
Kernel writeback tests should exercise dirtying, background writeback, sync writeback, BDI unregister, and cgroup writeback creation/offline. Lockdep and KCSAN are useful for list/refcount races. Debugfs or tracepoint observations should show correct `wb_reason` and bandwidth updates.
