<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/quota.c

## Purpose
`quota.c` implements GFS2 clustered quota accounting and quota control. It caches quota records in per-ID glocks with LVBs, records local per-node quota deltas in `quota_change<JID>` files, periodically syncs those deltas into the shared quota inode, checks allocations against limits, exposes VFS quotactl operations, and runs the `gfs2_quotad` background sync thread.

## Important APIs, types, and functions
External APIs include `gfs2_qa_get`, `gfs2_qa_put`, `gfs2_quota_hold`, `gfs2_quota_unhold`, `gfs2_quota_lock`, `gfs2_quota_unlock`, `gfs2_quota_check`, `gfs2_quota_change`, `gfs2_quota_sync`, `gfs2_quota_refresh`, `gfs2_quota_init`, `gfs2_quota_cleanup`, `gfs2_wake_up_statfs`, `gfs2_quotad`, `gfs2_qd_shrinker_init`, `gfs2_qd_shrinker_exit`, `gfs2_quota_hash_init`, and `gfs2_quotactl_ops`. Important internals include `qd_get`, `qd_alloc`, `qd_put`, slot and buffer helpers (`slot_get`, `bh_get`, `qdsb_get`), `do_qc`, `gfs2_adjust_quota`, `do_sync`, `update_qd`, `do_glock`, `need_sync`, `gfs2_get_dqblk`, and `gfs2_set_dqblk`.

## Control Flow
Quota data objects are hashed by `(sdp, kqid)` into an RCU hlist and linked on a per-superblock list plus a global LRU. `qd_get` first searches under RCU, allocates a new object and quota glock if needed, and inserts it under `qd_lock` plus a bucket lock. Objects use `lockref`; when their count reaches zero, they move to `gfs2_qd_lru` unless the journal is no longer live, in which case they are disposed.

Allocation paths call `gfs2_quota_lock_check` from the header or explicitly call `gfs2_quota_lock`. `gfs2_quota_hold` prepares qadata for current uid/gid and optional new uid/gid, obtains quota-change slots and buffers, and stores qd pointers on the inode. `gfs2_quota_lock` sorts qds to avoid deadlocks and locks each quota glock through `do_glock`, which reads from the LVB or refreshes from the quota inode under an exclusive quota glock. `gfs2_quota_check` compares requested/minimum allocation against hard and warning limits using LVB value plus local unsynced change. `gfs2_quota_change` updates the per-node quota-change buffer inside the active transaction through `do_qc`.

Unlock checks whether local changes are close enough to a limit to need immediate sync. Periodic or forced sync uses `gfs2_quota_sync`, which increments `sd_quota_sync_gen`, grabs batches of changed qds, maps their quota-change buffers, and calls `do_sync`. `do_sync` locks qd glocks and the quota inode, reserves allocation space if new quota records are needed, begins a transaction, applies each local delta to the shared quota record through `gfs2_adjust_quota`, subtracts the delta from `quota_change`, ends the transaction, flushes the quota inode glock, and advances each qd's sync generation. `gfs2_quota_init` scans the per-node quota-change file at mount, reconstructs changed qds and slot bitmap state, and zeros duplicate slots. `gfs2_quotad` periodically runs statfs sync and quota sync and wakes for forced statfs work.

## State and Persistence
Persistent state is split between the shared `quota` inode (`struct gfs2_quota` records indexed as user/group pairs) and the per-node `quota_change<JID>` inode (`struct gfs2_quota_change` slots). Runtime state includes the qd hash, qd LRU, per-qd glock/LVB cache, qd change counters, slot bitmap, qadata arrays on inodes, quota sync generation, and quiet/warning flags. Quota glock LVBs cache limit, warn, and usage values with `GFS2_MAGIC`.

## Dependencies and Integration Points
Quota code depends on glocks and quota glops, bmap/iomap, metadata I/O, transactions, log flushing, rgrp allocation reservation, inode hidden-file handling, VFS quota APIs, netlink quota warnings, shrinkers, RCU, list_lru, and mount options from `ops_fstype.c`. Allocation and ownership-changing paths in inode, bmap, file, xattr, dir, rgrp, and superblock code call into this API.

## Risks
Clustered quotas are intentionally fuzzy because local deltas are synced periodically, so enforcement can temporarily overrun limits. Correctness relies on transactionally updating quota-change slots with allocation changes; missed `gfs2_quota_change` calls would corrupt accounting. Lock ordering (`qd_lock -> bucket lock -> qd lockref -> LRU`, and qd sorting before glock acquisition) is deadlock-sensitive. Cleanup asserts journal liveness state and waits up to 60 seconds for qds. `gfs2_quota_init` duplicate-slot repair must write back dirty buffers. Page-boundary quota records and stuffed quota inode unstuffing require conservative transaction reservations.

## Test Signals
Signals include quota on/account/off/quiet modes, uid and gid hard/soft limit checks, warning period and quiet reset, allocation/free/change-owner flows, immediate sync near limits, periodic `quotad` sync, forced statfs wake, quotactl get/set, quota records crossing page or block boundaries, stuffed quota inode expansion, duplicate quota_change slot detection, shrinker reclamation, mount-time reconstruction of unsynced deltas, cleanup with live qd references, and multi-node overrun behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.c -->
