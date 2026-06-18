# Group Research: group_1001_linux_stable_sources_os_linux_linux_stable_fs_gfs2_lock_dlm_c_sourc_0773072fe839

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/lock_dlm.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/lock_dlm.c

Implements the `lock_dlm` clustered lock manager backend for GFS2. It translates GFS2 glock states and flags into DLM lock modes/flags, handles DLM AST/BAST callbacks, records lock timing statistics, and coordinates cluster journal recovery through DLM lockspace callbacks.

Key entry points are exposed through `gfs2_dlm_ops`: `gdlm_mount`, `gdlm_first_done`, `gdlm_recovery_result`, `gdlm_unmount`, `gdlm_put_lock`, `gdlm_lock`, and `gdlm_cancel`.

Important behavior:
- `gdlm_lock()` builds DLM resource names from glock type/number, computes conversion flags, tracks blocking requests, retries `-EBUSY`, and submits `dlm_lock()`.
- `gdlm_ast()` maps DLM completion statuses to GFS2 lock outcomes, clears initial lock state on first success, handles unlock completion by freeing dead glocks, and clears invalid LVBs.
- `gdlm_bast()` maps DLM blocking callback modes back to GFS2 callback states for demotion pressure.
- `gdlm_put_lock()` either skips unlock on lockspace teardown when safe or sends `dlm_unlock()` while preserving LVB updates for exclusive locks.
- Recovery uses `control_lock` and `mounted_lock` plus a control-lock LVB containing a generation number and jid bitmap.
- `gfs2_control_func()` propagates DLM failed-slot notifications into LVB bits, starts `gfs2_recover_set()` for pending journals, clears recovered bits, and thaws glocks when all recovery for the generation is complete.
- `control_mount()` distinguishes first mounter, normal mounter, and spectator cases; first mounters recover all journals before allowing others to proceed.
- DLM callbacks `gdlm_recover_prep`, `gdlm_recover_slot`, and `gdlm_recover_done` maintain generation and failed-journal arrays under `ls_recover_spin`.

Dependencies include Linux DLM APIs, GFS2 glock core, recovery workqueues, lock value blocks, and filesystem mount arguments. The main correctness risks are generation ordering, LVB bitmap consistency, lockspace teardown races, and preserving first-mounter recovery semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/lock_dlm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/log.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/log.c

Implements GFS2 journal space accounting, log reservation, AIL management, ordered write handling, revoke handling, log flush orchestration, and the `gfs2_logd` kernel thread.

Key exported functions include `gfs2_struct2blk`, `gfs2_log_is_empty`, `gfs2_log_release_revokes`, `gfs2_log_release`, `gfs2_log_try_reserve`, `gfs2_log_reserve`, `gfs2_write_log_header`, `gfs2_remove_from_journal`, `gfs2_log_flush`, `gfs2_log_commit`, `gfs2_ail1_flush`, `log_flush_wait`, `gfs2_add_revoke`, `gfs2_glock_remove_revoke`, `gfs2_flush_revokes`, `gfs2_ail_drain`, and `gfs2_logd`.

Important behavior:
- AIL1 tracks buffers that still need in-place writeback; AIL2 tracks transactions whose buffers have been written and whose log space can be released after tail movement.
- `gfs2_ail1_flush()` starts writeback via inode mappings, handles jdata holes, detects long stuck flushes, and withdraws on serious writeback errors.
- Reservation paths account for both journal blocks and revokes; non-logd callers preserve `GFS2_LOG_FLUSH_MIN_BLOCKS` so logd can still flush.
- `calc_reserved()` computes live reservation needs for metadata, journaled data, descriptor blocks, revokes, and headers.
- Ordered-data mode writes and waits on ordered inode mappings before committing the log header.
- `gfs2_write_log_header()` builds on-disk log headers with hashes, CRCs, sequence/tail/head metadata, local statfs/quota inode references, and block mapping.
- `__gfs2_log_flush()` serializes flushes, detaches the incore transaction, runs log-operation commit hooks, writes headers, drains AIL for sync/shutdown/freeze flushes, and handles withdraw cleanup.
- `log_refund()` merges completed transactions into `sd_log_tr`, recomputes actual reservation needs, and releases unused blocks.
- `gfs2_logd()` wakes on pinned/log pressure or periodic timeout, flushes journal blocks, and starts AIL writeback as thresholds are crossed.

The file is central to GFS2 crash consistency. Risk areas include reservation/refund balance, revoke accounting, withdraw paths during partial flush, AIL list locking, and ensuring ordered data reaches disk before the committing log header.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/log.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/log.h

Declares the public log-management interface used by GFS2 transaction, inode, glock, quota, mount, and recovery code.

Key contents:
- Defines `GFS2_LOG_FLUSH_MIN_BLOCKS` as the minimum space reserved for revoke/header work during flushes.
- Provides `gfs2_ordered_add_inode()`, which adds non-journaled-data inodes to the ordered write list when the filesystem is in ordered mode.
- Declares reservation, release, flush, commit, AIL, revoke, ordered-inode, and logd APIs implemented in `log.c`.

The header is a narrow contract for journal accounting and flush operations. Callers depend on its reservation functions to preserve log space invariants and on `gfs2_log_flush()`/`gfs2_log_commit()` for transaction durability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/lops.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/lops.c

Implements low-level journal operations for metadata buffers, journaled data buffers, and revoke records. It also provides shared journal I/O helpers, journal-head search, pin/unpin transitions, and replay handlers.

Key exported functions include `gfs2_pin`, `gfs2_log_incr_head`, `gfs2_log_bmap`, `gfs2_log_submit_write`, `gfs2_log_write`, `gfs2_find_jhead`, and `gfs2_drain_revokes`.

Important behavior:
- `gfs2_pin()` clears dirty state, marks buffers pinned, moves already-written AIL entries, and increments pinned-log accounting.
- `gfs2_unpin()` marks buffers dirty again after log write, attaches them to transaction AIL1, updates glock AIL membership, and handles rgrp clone/discard bookkeeping.
- Journal writes are batched in bios via `gfs2_log_get_bio()` and completed by `gfs2_end_log_write()`, which unlocks page-cache buffers or frees mempool pages.
- `gfs2_find_jhead()` scans mapped journal extents using large bio batches to locate the highest valid log header sequence.
- `gfs2_before_commit()` writes descriptor blocks followed by payload blocks, sorting buffers by disk block number and escaping journaled data whose first word matches `GFS2_MAGIC`.
- Metadata replay scans `GFS2_LOG_DESC_METADATA` records, checks revokes, copies log blocks back to in-place metadata buffers, validates metadata, and syncs the journal inode glock.
- Revoke commit writes revoke descriptor and continuation blocks; revoke replay builds an in-memory revoke list on pass 0 and clears it after pass 1.
- Journaled data replay handles `GFS2_LOG_DESC_JDATA`, including unescaping.
- `gfs2_log_ops[]` registers operation order: databuf, buf, revoke.

This file ties the abstract log flush/recovery code to concrete on-disk log descriptor formats. Risk areas include descriptor length/count accounting, buffer pin lifetime, escaped-buffer copy correctness, bio completion, and replay ordering across revoke and payload passes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/lops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/lops.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/lops.h

Defines the log-operation dispatch interface and declares core low-level journal helpers from `lops.c`.

Key contents:
- Exposes `gfs2_log_ops[]`, the array of registered log operation handlers.
- Declares log-head movement, journal block mapping, log write/submit, buffer pinning, journal-head search, and revoke drain helpers.
- Defines `buf_limit()` and `databuf_limit()` descriptor capacities.
- Provides inline dispatchers for `lo_before_commit`, `lo_after_commit`, `lo_before_scan`, `lo_scan_elements`, and `lo_after_scan`.

This header is the bridge between `log.c` flush/recovery orchestration and individual log operation implementations. Correctness depends on stable operation ordering and every operation tolerating passes/descriptors that do not belong to it.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/lops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/main.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/main.c

Implements GFS2 module initialization and teardown. It creates global caches, workqueues, shrinkers, mempools, debugfs/sysfs support, and registers the `gfs2` and `gfs2meta` filesystem types.

Important behavior:
- Initializes global qstrs for `.` and `..`, quota hash buckets, sysfs support, quota-data LRU, and glock subsystem.
- Creates slab caches for glocks, glock address spaces, inodes, bufdata, resource groups, quota data, qadata, and transactions.
- Initializes object constructors for inodes and glocks so embedded lists, locks, holders, resource reservations, and address spaces start in valid states.
- Registers the quota-data shrinker and allocates `gfs2_recovery_wq`, `gfs2_control_wq`, and `gfs2_freeze_wq`.
- Creates the page mempool used by log descriptor/header I/O.
- Registers debugfs, then `gfs2_fs_type` and `gfs2meta_fs_type`.
- Teardown reverses registration, destroys workqueues/LRU/mempool/caches, runs `rcu_barrier()`, and uninitializes sysfs.

The file owns process-wide resource lifetime. Risk areas are failure-label ordering in init and ensuring RCU-deferred quota data is drained before caches are destroyed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/meta_io.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/meta_io.c

Implements metadata address-space writeback, metadata buffer lookup/read helpers, metadata readahead, and journal wipe support for freed or deleted blocks.

Key exported functions include `gfs2_meta_new`, `gfs2_meta_read`, `gfs2_meta_wait`, `gfs2_getbuf`, `gfs2_journal_wipe`, `gfs2_meta_buffer`, and `gfs2_meta_ra`.

Important behavior:
- Defines `gfs2_meta_aops` and `gfs2_rgrp_aops`, both using buffer-backed dirty/invalidate/writepages/release/migrate operations.
- `gfs2_aspace_write_folio()` locks dirty mapped buffers, submits metadata writes with priority flags, starts/ends folio writeback, and redirties on nonblocking lock failure.
- `gfs2_getbuf()` maps a filesystem block into either a glock-specific address space or the global metadata address space, creating buffers when requested.
- `gfs2_meta_new()` prepares a new metadata buffer with uptodate state and `GFS2_MAGIC`.
- `gfs2_meta_read()` can issue the requested read plus one-block readahead, batching consecutive buffer heads into bios, and waits when `DIO_WAIT` is set.
- `gfs2_meta_wait()` validates read completion and reports I/O errors, including transaction-touched buffer diagnostics.
- `gfs2_journal_wipe()` removes freed ranges from AIL/journal state and clears metadata or jdata buffers from the journal.
- `gfs2_meta_buffer()` reads and validates a specific metadata type; `gfs2_meta_ra()` performs extent readahead with the tuned maximum.

This file is the common buffer-cache substrate for GFS2 metadata. Risk areas include buffer lifetime/refcounts, dirty/pinned journal interactions during block deletion, and avoiding stale metadata after withdraw.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/meta_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/meta_io.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/meta_io.h

Declares metadata I/O helpers and small buffer manipulation utilities.

Key contents:
- Inline helpers clear whole buffers, clear tails, and copy/zero buffer tails.
- Exposes `gfs2_meta_aops` and `gfs2_rgrp_aops`.
- Provides `gfs2_mapping2sbd()` for mapping metadata or inode address spaces back to `struct gfs2_sbd`.
- Declares metadata buffer creation/read/wait/get, journal wipe, typed metadata buffer lookup, and readahead APIs.
- Defines `REMOVE_JDATA` and `REMOVE_META` modes for journal removal.
- Defines `buffer_busy()` as dirty, locked, or pinned.

Callers use this header for safe metadata buffer access under glock protection. The major contract is that returned buffer heads carry references and must be released by callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/meta_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/ops_fstype.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/ops_fstype.c

Implements GFS2 filesystem type registration behavior: mount context parsing, superblock setup, lock protocol mounting, journal/statfs/quota/per-node initialization, remount/reconfigure, gfs2meta mounting, and superblock teardown.

Important behavior:
- `init_sbd()` allocates and initializes `struct gfs2_sbd`, waitqueues, locks, lists, counters, journal state, quota state, and default tune values.
- Superblock reading uses direct block-device I/O to avoid cached data, validates on-disk format/block sizes, derives pointer counts, hash sizing, directory reservation limits, and max metadata height.
- `init_names()` obtains lock protocol/table names from mount options or on-disk superblock.
- `gfs2_lm_mount()` selects `lock_nolock` or `lock_dlm`, parses hostdata, invokes the lock manager, and completes locking initialization.
- `init_locking()` acquires mount/live glocks and creates rename/freeze glocks.
- `init_sb()` locks and rereads the superblock, configures xattr handlers, block size, root dentry, and master dentry.
- `init_journal()` loads journal index entries, selects/locks this node’s journal, checks journal extents, initializes statfs inodes, and performs first-mounter or own-journal recovery.
- `init_per_node()` locates and locks the node-local quota-change file.
- `gfs2_fill_super()` ties all initialization together, creates workqueues/debug/sysfs entries, initializes inodes/rgrps/statfs/quota support, starts logd/quotad when writable, and makes the filesystem read-write when appropriate.
- Mount parameter parsing supports lock options, spectator/meta modes, ACLs, quota modes, data mode, discard, commit/statfs/quota intervals, barriers, rgrp LVBs, loccookie, and errors policy.
- `gfs2_reconfigure()` restricts immutable mount properties, handles ro/rw remounts, updates tune values, ACL/barrier flags, and emits online uevents.
- `gfs2meta` mounts attach to an existing GFS2 superblock and return the master directory.
- `gfs2_kill_sb()` flushes the log, drops root/master dentries, cooperatively evicts inodes, marks kill state, drains delete work, and kills the block superblock.

This file is the mount-state coordinator. Risk areas include unwind ordering, first-mount recovery boundaries, spectator read-only semantics, immutable remount validation, and teardown ordering while background work may still exist.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/ops_fstype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/quota.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/quota.c

Implements GFS2 clustered quota accounting. It maintains per-ID quota data objects, local per-node quota-change slots, quota LVB caching, periodic syncing into the global quota file, allocation checks, and VFS quotactl operations.

Important behavior:
- Quota changes are accumulated in node-local `quota_changeN` files and periodically synced to the shared quota file to reduce cluster contention.
- Quota data objects are hashed by superblock and `kqid`, protected by bucket locks and RCU, reference-counted with `lockref`, and reclaimable through `gfs2_qd_lru` and a shrinker.
- `slot_get/slot_put()` allocate local quota-change slots from `sd_quota_bitmap`; `bh_get/bh_put()` attach quota data to the correct quota-change buffer and slot.
- `gfs2_quota_hold()` collects current uid/gid plus optional ownership-change uid/gid quota data for an inode.
- `gfs2_quota_lock()` sorts quota data to avoid deadlocks, locks quota glocks, and refreshes LVBs from disk when stale or forced.
- `do_qc()` updates a local quota-change slot inside the current transaction and manages `QDF_CHANGE`, slot refs, and quiet warning state.
- `gfs2_quota_check()` enforces hard limits and soft-warning reporting unless quotas are off/account-only or the caller bypasses checks.
- `gfs2_quota_change()` records allocation/free deltas for matching user/group quota data.
- `do_sync()` locks all selected quota glocks plus the quota inode, reserves allocation/transaction space, applies local deltas into the shared quota file, subtracts them from local change slots, and flushes the log.
- `gfs2_quota_sync()` iterates dirty quota data in batches, advances `sd_quota_sync_gen`, and uses `do_sync()`.
- `gfs2_quota_init()` scans the node-local quota-change file at mount, reconstructs in-core dirty quota data and slot bitmap state, and repairs duplicate identifiers by zeroing duplicate slots.
- `gfs2_quota_cleanup()` disposes unused quota data and frees the slot bitmap after journal shutdown/no-recovery conditions.
- `gfs2_quotad()` periodically syncs statfs and quota data, wakes on forced statfs sync, and reports errors into the log subsystem.
- `gfs2_quotactl_ops` implements state query, get quota, set quota, and quota sync.

The main correctness risks are lock ordering across quota glocks and inode glocks, syncing local changes without losing deltas, quota-change slot lifetime, stale LVB refresh, and interaction with journal flush/withdraw paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/quota.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/quota.h

Declares the GFS2 quota subsystem API and quota helper constants.

Key contents:
- Defines `NO_UID_QUOTA_CHANGE` and `NO_GID_QUOTA_CHANGE` sentinels.
- Declares qadata allocation/refcount helpers, quota hold/unhold, quota lock/unlock, quota check/change, sync/refresh/init/cleanup, quotad, and statfs wakeup APIs.
- Provides `gfs2_quota_lock_check()`, which bypasses quota checks for quota-off or `CAP_SYS_RESOURCE`, otherwise locks quota data and enforces limits unless in account-only mode.
- Exposes `gfs2_quotactl_ops`, quota-data shrinker init/exit, global quota-data LRU, and quota hash initialization.

This header is used by allocation and mount paths to integrate quota checks with block reservation. Its important contract is that successful `gfs2_quota_lock_check()` may leave quota data locked and must be paired with `gfs2_quota_unlock()` by the caller.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/recovery.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/recovery.c

Implements journal replay and recovery work for dirty GFS2 journals. It reads journal blocks, manages replay revokes, validates log headers, scans descriptors through log operations, updates statfs state, writes clean journal headers, and reports recovery results to the lock manager.

Key exported functions include `gfs2_replay_read_block`, `gfs2_revoke_add`, `gfs2_revoke_check`, `gfs2_revoke_clean`, `__get_log_header`, `gfs2_recover_func`, `gfs2_recover_journal`, and `gfs2_log_pointers_init`.

Important behavior:
- `gfs2_replay_read_block()` maps journal logical blocks to disk blocks and reads metadata with readahead.
- Revoke tracking records the latest revoke position for a block and checks whether a replay block falls before/after the revoke across circular journal wrap.
- `__get_log_header()` validates magic/type/block number, legacy hash, CRC, and extracts sequence, flags, tail, block number, and local statfs deltas.
- `foreach_descriptor()` walks active journal descriptors from tail to head, tolerates embedded log headers, validates descriptor metadata, and dispatches scan handlers for each replay pass.
- Recovery uses two passes: pass 0 collects revokes; pass 1 replays metadata and journaled data not revoked.
- `recover_local_statfs()` applies journal-header local statfs deltas to the master statfs inode and zeroes the recovered journal’s local statfs inode.
- `clean_journal()` writes an unmount/recovery log header to mark replay complete.
- `gfs2_recover_func()` acquires journal locks for remote journals, checks read-only/frozen constraints, runs replay under `sd_log_flush_lock`, initializes log pointers for this node’s own journal, emits uevents, and reports success or gave-up status to the lock manager.
- `gfs2_recover_journal()` queues recovery work and optionally waits for completion.
- `gfs2_log_pointers_init()` sets log sequence/head/tail/flush pointers from the discovered journal head.

Risk areas include replay under freeze/read-only conditions, circular revoke math, descriptor scan bounds, statfs recovery idempotence, and coordinating remote journal locks with DLM recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/recovery.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/recovery.h

Declares the journal recovery interface and exposes the global recovery workqueue.

Key contents:
- Declares `gfs2_recovery_wq`.
- Defines `gfs2_replay_incr_blk()`, wrapping a journal block pointer at `jd_blocks`.
- Declares replay block read, revoke add/check/clean, journal recovery queueing, recovery work function, log-header validation, and log-pointer initialization APIs.

This header is consumed by mount, DLM recovery, log-operation replay, and journal code. Its central invariant is that all journal block iteration must wrap using the journal descriptor’s block count.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/recovery.h -->