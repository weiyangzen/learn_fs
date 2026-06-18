# sources/distributed-fs/ceph-client/block/blk-throttle.h

Purpose: declares the internal data structures and inline entry points for the block cgroup throttling policy implemented in `blk-throttle.c`. It also provides stubs when `CONFIG_BLK_DEV_THROTTLING` is disabled.

Important APIs and types: `struct throtl_qnode` holds per-source BPS and IOPS bio lists and pins its owning throttling group. `struct throtl_service_queue` contains parent linkage, read/write qnode lists, queued counts, an rbtree of active child groups, first dispatch time, and the pending timer. `enum tg_state_flags` records pending, queue-empty transition, IOPS-empty transition, and canceling state. `struct throtl_grp` embeds `blkg_policy_data` first, owns service queues, qnodes, limits, rule flags, slice counters, and rwstats. Public helpers are `pd_to_tg()`, `blkg_to_tg()`, `blk_throtl_activated()`, `blk_should_throtl()`, and `blk_throtl_bio()`.

Control flow: callers use `blk_throtl_bio()` from the bio submission path. The inline first checks whether the queue has an active throttling policy, updates legacy cgroup accounting when needed, tests inherited BPS/IOPS rule flags, and calls `__blk_throtl_bio()` only when throttling can apply. This keeps the hot path cheap for queues or cgroups without limits.

State and persistence: the header defines runtime-only objects that are allocated per `blkcg_gq` and per request queue. Rule flags cache whether a group or ancestor has limits, and stats accumulate in blkcg rwstat objects. No state is persisted outside kernel memory and cgroupfs-visible values.

Dependencies and integration points: depends on `blk-cgroup-rwstat.h`, blkcg policy plumbing, bio flags, cgroup default hierarchy detection, `request_queue->td`, and the `blkcg_policy_throtl` object. The first-member layout of `struct throtl_grp` is required by policy-data conversions.

Risks and test signals: layout or flag changes can break the implementation file, cgroup accounting, or queue teardown. `blk_should_throtl()` must not double-account legacy stats and must respect already BPS-throttled bios. Test with throttling configured and unconfigured, disabled config builds, cgroup v1/v2 accounting, and mixed BPS/IOPS limits.
