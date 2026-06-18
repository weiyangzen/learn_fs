# subset-b-005803 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_ail.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_ail.c

## Purpose
`xfs_trans_ail.c` implements the XFS Active Item List, the ordered list of dirty log items whose on-disk metadata writeback controls log tail advancement. It also runs `xfsaild`, the background thread that pushes dirty metadata buffers toward disk so log space can be reclaimed.

## Important APIs, types, and functions
The file operates on `struct xfs_ail`, `struct xfs_log_item`, and `struct xfs_ail_cursor` from `xfs_trans_priv.h`. Public entry points include `xfs_trans_ail_init`, `xfs_trans_ail_destroy`, `xfs_ail_min_lsn`, `xfs_trans_ail_update_bulk`, `xfs_trans_ail_insert`, `xfs_ail_delete_one`, `xfs_trans_ail_delete`, `xfs_ail_update_finish`, `xfs_ail_push_all_sync`, and AIL cursor helpers. The daemon path centers on `xfsaild`, `xfsaild_push`, `xfsaild_process_logitem`, `xfsaild_push_item`, and `xfs_ail_calc_push_target`.

## Control flow
Mount setup allocates an AIL, initializes lists, locks, wait queues, delayed-write buffer list, and starts `xfsaild`. Committed log items are inserted or repositioned by `xfs_trans_ail_update_bulk` under `ail_lock` in LSN order. Deletion clears `XFS_LI_IN_AIL`, invalidates active cursors, recalculates the log tail if the minimum LSN changed, and wakes log-space waiters. `xfsaild` sleeps when no work exists, computes a push target based on log occupancy or explicit push-all requests, walks the AIL with cursor invalidation protection, calls item `iop_push` methods, submits delayed write buffers, and backs off according to lock contention, pinned items, or flushing pressure.

## State and persistence
AIL state is in-memory but represents committed log items whose metadata has not reached stable storage. Persistent consequences appear through log tail updates, buffer writeback, and recovery ordering. `ail_target`, `ail_last_pushed_lsn`, `ail_log_flush`, cursor invalidation bits, and `ail_buf_list` are runtime control state. `atomic64_set(&log->l_tail_lsn)` and `l_tail_space` update log accounting after AIL changes.

## Dependencies and integration points
The file integrates with the xlog/CIL layer, item operation vectors, buffer delayed writeback, kthreads/freezer, XFS stats and tracepoints, error tags, shutdown handling, and log-space wakeups. Items without push callbacks are treated as pinned so the CIL can be forced.

## Risks and test signals
Risk concentrates in list ordering, cursor invalidation under item removal, lock dropping by item push callbacks, use-after-free after `iop_push`, failed buffer resubmission ordering, and tail LSN correctness. Test signals include debug AIL ordering checks, forced pinned-item errortags, shutdown during delayed write submission, push-all sync drain, concurrent insert/delete traversal, log-space exhaustion workloads, and metadata IO error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_ail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_buf.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_buf.c

## Purpose
`xfs_trans_buf.c` attaches metadata buffers to transactions, records which buffer byte ranges or semantic types must be logged, and controls buffer lifetime while transactions commit, cancel, or invalidate blocks.

## Important APIs, types, and functions
Important entry points are `xfs_trans_get_buf_map`, `xfs_trans_read_buf_map`, `xfs_trans_getsb`, `xfs_trans_getrtsb`, `xfs_trans_bjoin`, `xfs_trans_brelse`, `xfs_trans_bdetach`, `xfs_trans_bhold`, `xfs_trans_bhold_release`, `xfs_trans_dirty_buf`, `xfs_trans_log_buf`, `xfs_trans_binval`, `xfs_trans_inode_buf`, `xfs_trans_stale_inode_buf`, `xfs_trans_inode_alloc_buf`, `xfs_trans_ordered_buf`, `xfs_trans_buf_set_type`, `xfs_trans_buf_copy_type`, and `xfs_trans_dquot_buf`. It mainly manipulates `struct xfs_buf`, `struct xfs_buf_log_item`, and transaction item lists.

## Control flow
Buffer lookup first searches the transaction item list for an already joined buffer and increments `bli_recur` if found. New buffers are read or allocated through the buffer cache, initialized with a buf log item, refcounted, and joined to the transaction. Logging a buffer marks the transaction dirty, sets log item dirty state, and records byte ranges. Invalidating a buffer marks it stale, clears logged data maps, sets cancel flags for recovery, and keeps the item dirty until commit/cancel can safely resolve pins.

## State and persistence
Runtime state includes `bp->b_transp`, buffer lock recursion, log item refcounts, stale/hold/logged/ordered/inode-buffer flags, buffer iodone callbacks, and per-format dirty bitmaps. Persistent effects are journal records describing metadata buffer contents, cancellation records for freed buffers, and buffer type tags that guide log recovery.

## Dependencies and integration points
This code is the transaction-facing side of the XFS buffer cache and buf item subsystem. It integrates with metadata verifiers, shutdown handling, log recovery buffer type flags, inode and dquot buffer iodone callbacks, reflink/ordered buffer semantics, and quota buffer replay filtering.

## Risks and test signals
Risk areas include recursive buffer accounting, stale-buffer relogging, freeing clean log items too early, missing verifier errors on buffers already in a transaction, ordered buffer misuse after data ranges were logged, and recovery type flag mismatches. Test signals include repeated get/read of the same buffer in one transaction, dirty then brelse behavior, binval of pinned buffers, shutdown read paths, dquot/inode buffer recovery, and ordered-buffer assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_dquot.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_dquot.c

## Purpose
`xfs_trans_dquot.c` stages quota reservations and usage deltas inside transactions, applies them to in-core dquots at commit time, unwinds reservations on abort, and performs quota limit enforcement for user, group, and project quotas.

## Important APIs, types, and functions
Public functions include `xfs_trans_dqjoin`, `xfs_trans_log_dquot`, `xfs_trans_dup_dqinfo`, `xfs_trans_mod_dquot_byino`, `xfs_trans_mod_dquot`, `xfs_trans_apply_dquot_deltas`, `xfs_trans_unreserve_and_mod_dquots`, `xfs_trans_reserve_quota_bydquots`, `xfs_trans_reserve_quota_nblks`, `xfs_trans_reserve_quota_icreate`, `xfs_trans_free_dqinfo`, and `xfs_quota_reserve_blkres`. The central data structures are `struct xfs_dqtrx`, `struct xfs_dquot`, `struct xfs_trans`, and `struct xfs_quotainfo`.

## Control flow
Callers attach quota changes with `xfs_trans_mod_dquot` or the inode wrapper. Transaction commit locks affected dquots, joins their log items, applies block, realtime block, inode, and delayed-allocation deltas, adjusts default limits/timers, marks the dquot dirty, logs it, and releases any unused reservation. Transaction abort walks the same staged records and subtracts reservations without applying usage deltas. Reservation APIs enforce hard and soft limits, send quota netlink warnings, and unwind earlier user/group reservations if project quota reservation fails.

## State and persistence
`tp->t_dqinfo` is a transaction-scoped staging area. Dquot counters and reservation fields are in-core until the dquot log item is committed and written. Bigtime format can be enabled on non-root dquots at log time. Hook state exists only with `CONFIG_XFS_LIVE_HOOKS` and supports online fsck observation of quota updates.

## Dependencies and integration points
The file depends on quota core warning APIs, XFS dquot locking, quota defaults and timers, inode quota attachments, transaction item logging, health marking, and optional live hooks. It is used by allocation, inode creation, delayed allocation, chown, and realtime allocation paths.

## Risks and test signals
Risks include all-or-nothing reservation unwind, signed delta arithmetic, reservation-used math when allocations exceed reservation, lock ordering across multiple dquots, metadir/quota inode exclusions, soft-limit timer enforcement, and hook ordering. Test signals include user/group/project reservation failures at each stage, forced reservations, delayed allocation accounting, abort after partial reservation, live hook consumers, soft and hard limit warning delivery, and corruption detection when reserved drops below count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_dquot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_priv.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_priv.h

## Purpose
`xfs_trans_priv.h` declares private transaction and AIL interfaces shared among XFS transaction implementation files. It exposes internal structures and helpers that should not be part of the broader filesystem API.

## Important APIs, types, and functions
It defines `struct xfs_ail_cursor` and `struct xfs_ail`, declares transaction item helpers, superblock unreservation, AIL insert/update/delete/cursor functions, tail LSN assignment, and push helpers. Inline helpers include `xfs_ail_min`, `xfs_trans_ail_update`, `xfs_ail_push`, `xfs_ail_push_all`, `xfs_ail_get_push_target`, `xfs_ail_assign_tail_lsn`, and `xfs_trans_ail_copy_lsn`.

## Control flow
Callers include this header when they need to manipulate the AIL or private transaction item list directly. Cursor helpers document the invalidation protocol: removed items cause affected cursor pointers to be tagged so a traversal restarts safely. Push helpers wake the AIL daemon or set the push-all bit before waking it.

## State and persistence
The header declares in-memory state only. `struct xfs_ail` holds the log pointer, daemon task, sorted item list, active cursors, spinlock, push target, delayed-write buffers, and empty wait queue. `ail_head_lsn` and log-tail helpers affect persistent log recovery boundaries indirectly through the mounted log state.

## Dependencies and integration points
It bridges transaction core code, AIL daemon code, log item implementations, and log tail accounting. The 32-bit `xfs_trans_ail_copy_lsn` variant locks around 64-bit LSN copies to avoid torn reads.

## Risks and test signals
Risks include misuse of functions that release `ail_lock`, stale cursor assumptions, push-all bit handling, and cross-architecture torn LSN reads. Test signals are mostly indirect through AIL insert/delete stress, 32-bit builds, lockdep, and log tail movement tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.c

## Purpose
`xfs_verify_media.c` implements the privileged XFS media verification ioctl. It reads a caller-selected device range, advances the user-visible cursor over verified sectors, and can report real data loss to health monitoring and affected file owners when medium or protection errors occur.

## Important APIs, types, and functions
The exported entry point is `xfs_ioc_verify_media`. Internal helpers include `xfs_verify_media`, `xfs_verify_iosize`, `xfs_verify_alloc_folio`, `xfs_verify_media_error`, `xfs_verify_report_losses`, and `xfs_verify_report_data_lost`. It uses `struct xfs_verify_media`, `struct xfs_buftarg`, `struct bio`, rmap btree cursors, AG/RT group iteration, and `fserror_report_data_lost`.

## Control flow
The ioctl checks `CAP_SYS_ADMIN`, validates padding, flags, and target device, copies the request, and calls `xfs_verify_media`. Verification resolves data/log/realtime buftarg, clamps the end to the device size, checks logical-sector alignment, allocates a folio and one-bvec bio, and submits synchronous reads until done, interrupted, or a bio error occurs. Reportable errors trigger tracepoints, healthmon notifications, and if rmapbt exists, reverse-map walks to identify file extents whose data overlapped the failed media range.

## State and persistence
The operation is mostly stateless. It mutates the user request by updating `me_start_daddr`, possibly `me_end_daddr`, and `me_ioerror`. Persistent filesystem metadata is not changed except for health/sick markers when rmap records reveal damaged bmbt blocks, attr forks, or xattrs.

## Dependencies and integration points
It integrates with the block layer, XFS healthmon, reverse mapping btrees, AG and realtime group metadata, inode cache lookup, file-error reporting, and tracepoints. It depends on rmapbt for file-level data-loss attribution.

## Risks and test signals
Risks include off-by-one conversion between daddr, FSB, RTB, and group block numbers, false attribution when `xfs_iget` fails, alignment rejection, large allocation fallback, and interruption semantics. Test signals include unaligned requests, ranges past device end, data/log/rt devices, injected `BLK_STS_MEDIUM`, `BLK_STS_PROTECTION`, and transient errors, rmapbt on/off, realtime ranges, and fatal signal interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.h

## Purpose
`xfs_verify_media.h` is the small declaration header for the XFS media verification ioctl implementation.

## Important APIs, types, and functions
It forward-declares `struct xfs_verify_media` and declares `xfs_ioc_verify_media(struct file *file, struct xfs_verify_media __user *arg)`.

## Control flow
The header is included by ioctl dispatch code that needs to hand a userspace `xfs_verify_media` request to the implementation in `xfs_verify_media.c`.

## State and persistence
The header has no state and performs no persistence. It preserves the userspace pointer annotation for sparse checking.

## Dependencies and integration points
It integrates the ioctl layer with the media verification implementation while avoiding broader include dependencies.

## Risks and test signals
Risks are limited to declaration drift with the implementation or UAPI structure. Test signals come from successful build coverage and ioctl tests that compile through this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.c

## Purpose
`xfs_xattr.c` adapts XFS attribute fork operations to the Linux VFS xattr API, including get/set/list handlers, namespace prefix translation, ACL name translation, quota attachment, and optional debug-only logged xattr assistance.

## Important APIs, types, and functions
The key exported symbols are `xfs_attr_change`, `xfs_xattr_handlers`, and `xfs_vn_listxattr`. Internal helpers include `xfs_attr_grab_log_assist`, `xfs_attr_want_log_assist`, `xfs_xattr_get`, `xfs_xattr_flags_to_op`, `xfs_xattr_set`, `xfs_xattr_put_listent`, and `__xfs_xattr_put_listent`. VFS handlers cover user, trusted/root, and security namespaces.

## Control flow
Get builds `xfs_da_args` from the VFS handler and calls `xfs_attr_get`. Set/remove attaches quota state, allows missing-name removal, optionally enables log-assisted xattrs in debug LARP mode, fills attr geometry/fork/owner/hash, and calls `xfs_attr_set` with reserve-pool permission for root/security attributes. List walks XFS attributes and emits VFS-prefixed names, hiding private namespaces and trusted names from callers without `CAP_SYS_ADMIN`, while translating legacy SGI ACL names to `system.posix_acl_*`.

## State and persistence
Persistent state lives in the inode attr fork and, when debug LARP is enabled, in the superblock log-incompat feature bit `XFS_SB_FEAT_INCOMPAT_LOG_XATTRS`. Runtime state is limited to list contexts, op flags, and quota attachments.

## Dependencies and integration points
It depends on XFS attr code, directory-attribute args, ACL handling, quota attachment, log feature updates, VFS xattr handlers, capabilities, and POSIX ACL xattr names.

## Risks and test signals
Risks include namespace filtering leaks, ACL name translation mistakes, using reserve blocks too broadly or too narrowly, attr fork zap handling, log-incompat enablement on unsupported filesystems, and list buffer sizing. Test signals include all xattr namespaces, ACL get/list behavior, unprivileged trusted listing, create/replace/remove flags, ENOSPC with security attrs, shutdown handling, and debug logged-xattr mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.h

## Purpose
`xfs_xattr.h` declares the XFS xattr bridge used by VFS-facing inode code and other XFS attribute callers.

## Important APIs, types, and functions
It forward-declares `enum xfs_attr_update`, declares `xfs_attr_change`, and exposes `xfs_xattr_handlers`.

## Control flow
VFS inode setup can install `xfs_xattr_handlers`, while attr mutation code can call `xfs_attr_change` for set/create/replace/remove operations with initialized `xfs_da_args`.

## State and persistence
The header has no state. The declared implementation mutates persistent inode attribute forks and possibly log-incompat feature state.

## Dependencies and integration points
It sits between generic inode/xattr setup and `xfs_xattr.c`, avoiding direct inclusion of the full implementation.

## Risks and test signals
Risks are limited to declaration mismatch and handler registration errors. Build coverage plus VFS xattr tests exercise it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.c

## Purpose
`xfs_zone_alloc.c` implements the zoned realtime allocator for XFS. It discovers and tracks realtime groups as zones, selects open zones for writeback, submits zone append or conventional writes, remaps completed writes into file data forks, accounts reclaimable space, and mounts/unmounts zoned allocator state.

## Important APIs, types, and functions
Public functions include `xfs_open_zone_put`, `xfs_zoned_have_reclaimable`, `xfs_zoned_end_io`, `xfs_zone_free_blocks`, `xfs_open_zone`, `xfs_zone_alloc_and_submit`, `xfs_zoned_wake_all`, `xfs_zone_rgbno_is_valid`, `xfs_mount_zones`, and `xfs_unmount_zones`. Important internal helpers handle open-zone initialization, reclaim buckets, zone selection, inode zone caching, write pointer discovery, open-zone limits, and mount-time validation.

## Control flow
Mount requires an RT device, rtgroups, rmapbt, `rextsize == 1`, and enough zones. It allocates `m_zone_info`, reports each block zone or derives conventional write pointers from rmap, marks empty zones free, restores partially written zones as open, buckets reclaimable full zones, clamps open-zone limits, adjusts writeback granularity, and starts GC. Writeback selects a cached or list-managed open zone by write-life hint and packing policy, reserves a range under `oz_alloc_lock`, splits ioends at allocation or zone-append boundaries, and submits bios. Completion calls `xfs_zoned_end_io`, which transactions the new mapping, frees overwritten extents or decrements refcounts, increments rmap used/written counters, and skips speculative GC writes if another writer won the race.

## State and persistence
Runtime state is `struct xfs_zone_info`, open-zone refs, per-inode cached `i_private` zone pointers, free-zone xarray marks, used-bucket bitmaps, reset lists, and free counters. Persistent accounting is stored in realtime rmap inode `i_used_blocks` and file bmaps. Device write pointers persist on zoned media; conventional zones approximate them from rmap after mount.

## Dependencies and integration points
The file integrates with iomap writeback, realtime groups, rmap btrees, bmap and refcount code, free counters, GC, block zone APIs, write-life hints, inode cache lifetime, XFS tracepoints, and mount option `max_open_zones`.

## Risks and test signals
Risks include open-zone ref leaks, stale inode cached zones, zone append sector reporting, speculative GC/user write races, reclaim bucket drift, free counter inconsistency, conventional-zone write pointer approximation after power loss, and open-zone deadlocks. Test signals include sequential and conventional zoned devices, mount after unclean shutdown, tiny open-zone limits, write-life hint colocation, small-file pack-tight workloads, full-zone transitions, freeing blocks from open versus closed zones, and bio split failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.h

## Purpose
`xfs_zone_alloc.h` declares the public zoned XFS allocation interface used by iomap writeback, realtime free-space accounting, mount/unmount, stats, and garbage collection control paths.

## Important APIs, types, and functions
It defines `struct xfs_zone_alloc_ctx` with an open-zone pointer and reserved block count, reservation flags `XFS_ZR_GREEDY`, `XFS_ZR_NOWAIT`, and `XFS_ZR_RESERVED`, and declarations for zoned space reserve/unreserve, availability updates, write submission, end-io remap, block free, open-zone put, wakeups, block-validity checks, stats, default reserved blocks, and mount/GC lifecycle.

## Control flow
Callers reserve zoned realtime space into an allocation context, submit writes via `xfs_zone_alloc_and_submit`, complete them through `xfs_zoned_end_io`, and unreserve any unused context state. Mount code calls `xfs_mount_zones` only when realtime support is present; otherwise stubs reject zoned mounting.

## State and persistence
The header has no storage, but its APIs manage open-zone references, free counters, rmap used counters, and persistent file mappings.

## Dependencies and integration points
It links XFS writeback, realtime allocation, zoned GC, sysfs/stat output, and mount feature checks. The `CONFIG_XFS_RT` conditional prevents accidental zoned operation without realtime support.

## Risks and test signals
Risks include caller leaks of `open_zone`, mismatched reserve/unreserve flags, and build behavior with `CONFIG_XFS_RT` disabled. Tests should cover reserve failure unwinds, nowait behavior, and non-RT build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_gc.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_gc.c

## Purpose
`xfs_zone_gc.c` implements background garbage collection for zoned XFS. It evacuates live realtime extents from partially used zones into reserved GC zones, remaps file data after successful IO, and resets zones that become empty.

## Important APIs, types, and functions
Public entry points are `xfs_zoned_need_gc`, `xfs_zone_gc_reset_sync`, `xfs_zone_gc_start`, `xfs_zone_gc_stop`, `xfs_zone_gc_wakeup`, `xfs_zone_gc_mount`, and `xfs_zone_gc_unmount`. Internal state includes `struct xfs_zone_gc_data`, `struct xfs_gc_bio`, and `struct xfs_zone_gc_iter`. Key helpers query and sort rmap records, pick victims from used buckets, select or steal GC target zones, allocate reserved GC blocks, pipeline read/write/reset bios, and finish remaps through `xfs_zoned_end_io`.

## Control flow
The GC kthread sleeps until space thresholds or reset work require action. It drains completed reset bios, completed writes, completed reads, and then starts new chunks. Victim selection walks reclaimable buckets from least used upward and avoids zones already under GC. Rmap records are gathered in batches, sorted by owner and offset, read into a scratch ring, written to a GC target zone with zone append splitting when needed, then remapped after direct IO/layout exclusion confirms no competing file writer invalidated the old mapping. Empty zones are flushed, log-forced, reset or discarded, marked free, and credited back to availability.

## State and persistence
Runtime state includes the scratch folio ring, bioset, reading/writing/resetting lists, victim iterator, GC target open zone, `rtg_gccount`, and `zi_reset_list`. Persistent effects include new file bmap entries, freed old extents, rmap used-counter updates, log-forced rmap state before reset, and hardware zone reset/discard state.

## Dependencies and integration points
It integrates with rtrmapbt, inode cache, bmap/remap code in `xfs_zone_alloc.c`, block zone reset/append/discard, memalloc NOFS, freezer/parkable kthreads, errortags, XFS stats, and zoned free-counter reservations.

## Risks and test signals
Risks include data movement races with user writes, reflink incompatibility, scratch ring wrap, zone append split alignment, stealing open zones after unclean shutdown, reserved-pool exhaustion, failure to decrement `rtg_gccount`, reset ordering before log persistence, and remount/shutdown wakeups. Test signals include low-space GC thresholds, tiny GC target capacity, injected read/write/reset failures, deleted inode rmaps, direct IO racing GC, mount after interrupted GC, and non-sequential conventional reset fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_info.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_info.c

## Purpose
`xfs_zone_info.c` renders zoned XFS runtime allocator and GC state into a seq_file statistics view.

## Important APIs, types, and functions
The exported function is `xfs_zoned_show_stats`. Helpers include `xfs_write_hint_to_str`, `xfs_show_open_zone`, and `xfs_show_full_zone_used_distribution`.

## Control flow
The stats function prints user and reserved realtime free counters, whether reservations or GC are required, total/free/open zone counts, each open zone with write pointer, written blocks, used blocks, write hint, and GC marker, then prints the distribution of fully written reclaimable zones by used-block bucket plus inferred completely full zones.

## State and persistence
It reads live in-memory state from `m_zone_info`, free counters, open-zone lists, atomic free-zone count, and used-bucket bitmaps. It does not mutate persistent state.

## Dependencies and integration points
It depends on `seq_file`, zoned allocator private structures, realtime group helpers, and `xfs_zoned_need_gc`. It is used by XFS stats/debug reporting paths that include zoned-specific output.

## Risks and test signals
Risks include reporting inconsistent snapshots while zones change, arithmetic underflow when deriving full zones, and lock coverage around open-zone and bucket lists. Test signals include reading stats during concurrent writeback, GC, reset, mount with no open zones, and varied write-life hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_priv.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_priv.h

## Purpose
`xfs_zone_priv.h` defines private zoned allocator structures shared by zone allocation, garbage collection, reservations, and stats code.

## Important APIs, types, and functions
It defines `struct xfs_open_zone`, `XFS_ZONE_USED_BUCKETS`, and `struct xfs_zone_info`. It declares `xfs_open_zone`, `xfs_zone_gc_reset_sync`, `xfs_zoned_need_gc`, `xfs_zoned_have_reclaimable`, `xfs_zone_gc_mount`, `xfs_zone_gc_unmount`, and `xfs_zoned_resv_wake_all`.

## Control flow
Open zones are tracked in a mount-level list, refcounted, and tied to realtime groups. `oz_allocated` advances when writeback reserves blocks; `oz_written` advances at write completion under the rmap inode lock. `xfs_zone_info` coordinates open-zone limits, free-zone counts, reservation waiters, GC thread, reset list, and reclaimable-zone buckets.

## State and persistence
All structures are in-memory. They mirror persistent/device state in rmap used counters and zone write pointers but are rebuilt at mount. RCU frees open zones after refs drop so cached inode pointers can be looked up safely.

## Dependencies and integration points
The header is private to zoned XFS implementation files and depends on list heads, atomics, wait queues, spinlocks, task structs, realtime groups, and write-life hints.

## Risks and test signals
Risks include incorrect lock ownership around `oz_written`, open-zone list count drift, reset-list races, bucket bitmap leaks, and cached pointer lifetime mistakes. Test signals include lockdep, RCU stress, mount/unmount under active writeback, GC with reservation waiters, and stats while zones transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_space_resv.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_space_resv.c

## Purpose
`xfs_zone_space_resv.c` manages zoned realtime free-space reservations. It separates total user-fillable realtime extents from immediately writable extents so user writers cannot consume the GC and reset reserve needed to make future progress.

## Important APIs, types, and functions
Public functions include `xfs_zoned_default_resblks`, `xfs_zoned_resv_wake_all`, `xfs_zoned_add_available`, `xfs_zoned_space_reserve`, and `xfs_zoned_space_unreserve`. Internal pieces include `struct xfs_zone_reservation`, `xfs_zoned_space_wait_error`, `xfs_zoned_reserve_available`, and `xfs_zoned_reserve_extents_greedy`.

## Control flow
Reservation first decrements `XC_FREE_RTEXTENTS`, optionally flushes inodegc, and optionally greedily shrinks short writes to remaining space. It then decrements `XC_FREE_RTAVAILABLE`; if unavailable and waiting is allowed, it queues the task on `zi_reclaim_reservations`, wakes GC when needed, sleeps until enough space appears or shutdown/signal/no-reclaimable conditions occur, and removes the waiter. Unreserve returns both total and immediately available counters and drops any held open-zone reference.

## State and persistence
Reservations are in-memory and per task or allocation context. Free counters are runtime mount accounting backed by filesystem metadata changes elsewhere. Default reserved block calculations reserve zones for GC, block zeroing, one free zone, and persistent `sb_rtreserved`.

## Dependencies and integration points
It depends on zoned allocator private state, free-counter helpers, inodegc, GC running state, wakeups from GC reset completion, and mount superblock reserve fields.

## Risks and test signals
Risks include starvation or unfair wake ordering, counter leaks on failure unwind, nowait returning the wrong errno, greedy reservations racing other writers, sleeping while no GC progress is possible, and reserved-pool misuse. Test signals include NOWAIT and RESERVED callers, signal interruption, shutdown wakeups, no reclaimable zones, inodegc freeing space, concurrent waiters, and ENOSPC under tiny zone counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_space_resv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/zonefs/Kconfig

## Purpose
`fs/zonefs/Kconfig` declares the kernel configuration option for building zonefs, a simple filesystem that exposes zones of a zoned block device as files.

## Important APIs, types, and functions
It defines `CONFIG_ZONEFS_FS` as a tristate option named "zonefs filesystem support". It depends on `BLOCK` and `BLK_DEV_ZONED`, and selects `FS_IOMAP` and `CRC32`.

## Control flow
Kconfig controls whether `fs/zonefs` is omitted, built in, or built as a module. Selecting the option ensures iomap helpers and CRC32 support are present for file IO and superblock checksum validation.

## State and persistence
No runtime state exists here. The selected config determines whether zonefs can mount on-disk zonefs-formatted zoned devices.

## Dependencies and integration points
It integrates zonefs into the kernel filesystem build menu and expresses hard dependencies on zoned block device infrastructure.

## Risks and test signals
Risks are missing dependencies when source files use iomap or CRC helpers, or accidental enablement without zoned block support. Test signals include allmodconfig, built-in, module, and dependency-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/Makefile -->
# sources/distributed-fs/ceph-client/fs/zonefs/Makefile

## Purpose
`fs/zonefs/Makefile` describes how the zonefs filesystem object is built.

## Important APIs, types, and functions
It adds `-I$(src)` to `ccflags-y`, builds `zonefs.o` when `CONFIG_ZONEFS_FS` is enabled, and links `super.o`, `file.o`, and `sysfs.o` into the composite object.

## Control flow
The local include path lets generated trace include directives find `trace.h`. The composite object ties mount/superblock logic, file operations, and sysfs support into one filesystem module or built-in object.

## State and persistence
No runtime state exists in the makefile.

## Dependencies and integration points
It connects the Kconfig option to the kbuild system and supports the tracepoint include layout used by `super.c`.

## Risks and test signals
Risks include omitting a new source file from `zonefs-y` or breaking trace header include resolution. Test signals are clean module and built-in builds with tracing enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/file.c -->
# sources/distributed-fs/ceph-client/fs/zonefs/file.c

## Purpose
`zonefs/file.c` implements zonefs file IO. It maps zone files to raw block device sectors through iomap, enforces sequential-zone append semantics, handles truncate-to-reset/finish operations, tracks write-open zones, and reacts to IO errors.

## Important APIs, types, and functions
Exports are `zonefs_file_aops`, `zonefs_file_operations`, and `zonefs_file_truncate`. Key helpers include read/write iomap begin functions, folio read/readahead/writeback operations, `zonefs_file_fsync`, mmap prepare/page_mkwrite, direct and buffered write paths, direct read completion, splice read, sequential write open/close, and file open/release.

## Control flow
Reads map written bytes as `IOMAP_MAPPED` and reads past EOF as holes. Conventional-zone writes can use buffered writeback and shared writable mmap. Sequential-zone writes must be direct, block-size aligned, and positioned at `z_wpoffset`; append writes rewrite `ki_pos` to the write pointer. The write path advances `z_wpoffset` before IO and completion grows inode size after successful direct IO; failures call `zonefs_io_error` to resync with hardware. Truncating sequential files to zero issues zone reset; truncating to capacity issues zone finish.

## State and persistence
Per-inode state is `i_truncate_mutex`, `i_wr_refcnt`, inode size, and `struct zonefs_zone` fields such as `z_wpoffset` and open/active flags. Persistent state is mostly the block device zone condition and write pointer; zonefs has no per-file metadata beyond the formatted superblock and in-memory zone table.

## Dependencies and integration points
It depends on iomap buffered/direct IO, block device flushes, zone management operations from `super.c`, VFS locks, mmap invalidate locks, swap activation, large folios, and tracepoints.

## Risks and test signals
Risks include sequential write reordering, async NOWAIT semantics, partial direct IO, stale `z_wpoffset` after errors, truncation races with mmap/read/write, explicit-open accounting leaks, full-zone close handling, and conventional writeback accidentally used on sequential zones. Test signals include direct append writes, misaligned writes, IOCB_NOWAIT, buffered conventional writes, mmap writes, reset/finish truncate, fsync, splice read, swapfile activation, and injected zone write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/super.c -->
# sources/distributed-fs/ceph-client/fs/zonefs/super.c

## Purpose
`zonefs/super.c` implements zonefs mount, superblock validation, zone discovery, inode and directory synthesis, mount options, error recovery, statfs, and module registration.

## Important APIs, types, and functions
Important exported functions are `zonefs_inode_account_active`, `zonefs_inode_zone_mgmt`, `zonefs_i_size_write`, `zonefs_update_stats`, `__zonefs_io_error`, `zonefs_dir_inode_operations`, and `zonefs_dir_operations`. Internal paths include superblock CRC validation, fs_context parsing, zone report callbacks, zone group initialization, lookup/readdir, inode allocation cache, fill/kill super, and filesystem registration.

## Control flow
Mount verifies the block device is zoned, allocates `zonefs_sb_info`, sets block size to zone write granularity, reads and checks the on-disk zonefs superblock, applies feature flags, reports all zones, groups them into `cnv` and `seq` directories, optionally aggregates contiguous conventional zones, closes initially open sequential zones, creates the synthetic root and group directory inodes, and registers sysfs. Lookup parses numeric names inside group directories and uses sector-derived inode numbers. IO errors re-report the affected zone, update readonly/offline flags and inode modes, correct inode size/write pointer, and optionally remount read-only.

## State and persistence
Persistent state is the 4 KiB `struct zonefs_super` at block 0 with magic, crc, label, uuid, feature flags, uid/gid/permissions. Most file state is reconstructed from block zone reports at mount. Runtime state includes zone arrays, active/write-open counters, mount options, stats block counts, and sysfs kobject state.

## Dependencies and integration points
The file integrates with fs_context, block zone reporting/management, VFS inode/dentry/directory operations, iomap file ops from `file.c`, sysfs, CRC32, slab caches, quota transfer on setattr, and tracepoint definition.

## Risks and test signals
Risks include invalid zone reports, feature incompatibility, aggregated conventional zone condition handling, active/open counter drift, inode number collisions, mount option reconfigure behavior, IO-error policy confusion, readonly/offline mode transitions, and cleanup after partial mount failure. Test signals include malformed superblocks, unknown features, devices with mixed zone types, explicit-open limits, errors= modes, lookup/readdir correctness, setattr/truncate, remount option changes, and mount/unmount leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/sysfs.c -->
# sources/distributed-fs/ceph-client/fs/zonefs/sysfs.c

## Purpose
`zonefs/sysfs.c` exposes per-mounted-zonefs counters under the global `fs/zonefs` sysfs directory.

## Important APIs, types, and functions
Public functions are `zonefs_sysfs_register`, `zonefs_sysfs_unregister`, `zonefs_sysfs_init`, and `zonefs_sysfs_exit`. The read-only attributes are `max_wro_seq_files`, `nr_wro_seq_files`, `max_active_seq_files`, and `nr_active_seq_files`.

## Control flow
Module init creates the global `zonefs` kobject under `fs_kobj`. Mount registration names the superblock, initializes a per-superblock kobject with the attribute group, and records registration success. Unmount deletes and puts the kobject and waits for release completion. Attribute reads recover `zonefs_sb_info` from the kobject and emit stored limits or atomic counters.

## State and persistence
Sysfs state is runtime-only. It mirrors open and active sequential file accounting from `zonefs_sb_info` and disappears on unmount or module exit.

## Dependencies and integration points
It depends on kobjects, sysfs attributes, superblock sysfs naming, completions, atomics, and zonefs mount state. It is called from zonefs module init/exit and fill/kill super.

## Risks and test signals
Risks include kobject lifetime races, double unregister, missing release completion after failed init, and stale counter reads during concurrent file open/close. Test signals include mount/unmount loops, failed sysfs registration injection, concurrent reads while closing files, and module unload with mounted filesystems rejected elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/trace.h -->
# sources/distributed-fs/ceph-client/fs/zonefs/trace.h

## Purpose
`zonefs/trace.h` defines tracepoints for observing zonefs zone management, direct append/write-pointer behavior, and iomap mapping decisions.

## Important APIs, types, and functions
It declares `TRACE_SYSTEM zonefs` and trace events `zonefs_zone_mgmt`, `zonefs_file_dio_append`, and `zonefs_iomap_begin`. It uses `show_dev`, `blk_op_str`, zone sector information, inode numbers, offsets, lengths, and iomap addresses.

## Control flow
`super.c` defines `CREATE_TRACE_POINTS` before including this header, while other zonefs files include it for trace event declarations. The bottom `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` settings support trace generation from the local source directory.

## State and persistence
Tracepoints keep no filesystem state. They emit runtime diagnostic events when enabled.

## Dependencies and integration points
It depends on Linux tracepoint infrastructure, block operation names, blkdev types, and `zonefs.h`. It integrates with tracefs/perf/ftrace tooling.

## Risks and test signals
Risks include format mismatch, missing local include path, or dereferencing fields not valid at trace time. Test signals include building with tracing, enabling each event during zone management, direct writes, reads, and iomap operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/zonefs.h -->
# sources/distributed-fs/ceph-client/fs/zonefs/zonefs.h

## Purpose
`zonefs/zonefs.h` centralizes zonefs constants, on-disk format, in-memory zone/superblock structures, feature and mount option flags, helper accessors, logging macros, and cross-file declarations.

## Important APIs, types, and functions
It defines `enum zonefs_ztype`, `struct zonefs_zone`, `struct zonefs_zone_group`, `struct zonefs_inode_info`, `struct zonefs_super`, `enum zonefs_features`, mount option flags, and `struct zonefs_sb_info`. Inline helpers convert block zones to zonefs types, recover `ZONEFS_I` and `ZONEFS_SB`, test conventional/sequential zones, fetch an inode zone, wrap `zonefs_io_error`, and declare file, directory, super, and sysfs operations.

## Control flow
All zonefs C files use this header to share the same view of zone metadata and mount state. The on-disk superblock definition is size-checked at module init. Helpers guide file IO decisions, mount feature validation, and error handling.

## State and persistence
The persistent structure is `struct zonefs_super`, including magic, CRC, label, UUID, feature bits, optional UID/GID/permissions, and reserved padding. In-memory state tracks zone condition flags, write pointer offsets, per-group zone arrays, active/open counters, mount options, stats, and sysfs kobject lifetime.

## Dependencies and integration points
It integrates VFS inode/superblock types, block zoned definitions, UUIDs, kobjects, mutexes, and zonefs source files. It also encodes feature compatibility between mkzonefs format options and kernel mount behavior.

## Risks and test signals
Risks include on-disk structure layout drift, feature flag mismatch, incorrect mount option bit semantics, and lock-order assumptions around `i_truncate_mutex`. Test signals include `BUILD_BUG_ON` super size, endian/CRC mount tests, feature matrix mounts, and lockdep on truncate/IO paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/zonefs/zonefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/Kbuild -->
# sources/distributed-fs/ceph-client/include/Kbuild

## Purpose
`include/Kbuild` exports top-level kernel headers selected by kbuild for generated UAPI/header-test workflows. In this tree it delegates DRM header test coverage.

## Important APIs, types, and functions
The only entry is `obj-$(CONFIG_DRM_HEADER_TEST) += drm/`, which descends into the `include/drm` subdirectory when DRM header tests are enabled.

## Control flow
During a kbuild pass with `CONFIG_DRM_HEADER_TEST=y` or module-equivalent test settings, kbuild evaluates this file and includes the DRM header-test directory in the build graph.

## State and persistence
No runtime state or persistent filesystem state exists.

## Dependencies and integration points
It integrates the repository's top-level include directory with the kernel build system and the DRM header-test configuration.

## Risks and test signals
Risks are limited to build graph omissions or accidental inclusion of headers under the wrong config. Test signals include builds with `CONFIG_DRM_HEADER_TEST` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/Kbuild -->
