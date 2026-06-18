# Group Research: group_1118_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_qm_c_sources__8095c94cf9ea

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm.c

## Purpose
Implements core XFS quota manager lifecycle and quota accounting glue: quota inode discovery/creation, quotainfo setup/teardown, dquot cache purging and reclaim, inode dquot attach/detach, mount-time quotacheck, vnode operation helpers, and enforcement-boundary detection.

## Main APIs
- `xfs_qm_mount_quotas` initializes quota state at mount, creates/loads quota inodes, runs quotacheck when needed, and syncs superblock quota flags.
- `xfs_qm_unmount`, `xfs_qm_unmount_quotas`, and `xfs_qm_destroy_quotainfo` release dquots, quota inodes, shrinkers, radix trees, and locks.
- `xfs_qm_dqattach`, `xfs_qm_dqattach_locked`, and `xfs_qm_dqdetach` manage inode-held user/group/project dquot references.
- `xfs_qm_qino_load` and `xfs_qm_qino_alloc` load or create quota metadata inodes, including metadir quota files and legacy superblock quota inode fields.
- `xfs_qm_vop_dqalloc`, `xfs_qm_vop_chown`, `xfs_qm_vop_rename_dqattach`, and `xfs_qm_vop_create_dqattach` support create, chown, rename, and inode creation quota accounting.
- `xfs_inode_near_dquot_enforcement` detects whether an inode is near quota hard/soft/preallocation limits.

## Key Behavior
The dquot cache is organized as per-type radix trees plus an LRU shrinker. `xfs_qm_dquot_walk` batch-walks radix trees and restarts if busy dquots are skipped. Purge and reclaim paths avoid resurrecting dead dquots, wait for pins/flush locks where needed, detach attached buffers, remove AIL state, delete radix-tree entries, and update quota statistics.

Mount initialization creates `struct xfs_quotainfo`, initializes LRU and tree locks, loads or creates quota inodes, computes dquot chunk geometry, initializes expiry ranges for legacy or bigtime dquots, imports default limits and grace periods from id-0 dquots, registers the shrinker, and sets up live quota hooks.

Mount-time quotacheck resets all on-disk dquot counters, scans every non-quota and non-metadir inode, reloads incomplete unlinked inodes, counts data/realtime blocks, updates in-core dquots and attached dquot buffers, flushes all dirty dquots, writes buffers, and marks quota check flags. On failure it flushes inodegc, purges cached dquots, destroys quotainfo, resets superblock quota flags, and marks quotacheck health sick.

Quota inode handling supports both legacy superblock inode numbers and metadata-directory quota files. V4 group/project quota inode sharing is handled by loading the opposite field when separate project quota inode support is absent. Metadir filesystems prepare the superblock quota feature, create `/quotas` and per-type quota files, and retain the quota directory inode only when online scrub is enabled.

Vnode quota helpers attach dquots before metadata-changing operations, allocate destination dquots for ownership changes, transfer block/inode/realtime counts during chown, attach dquots to new inodes, and account delayed allocation reservations specially when ownership changes.

## Dependencies
Depends on dquot cache/flush helpers, transaction and log item APIs, inode walk and inodegc, quota metadata inode helpers, radix trees, list LRU shrinker, buffer delayed-write lists, superblock logging, health flags, realtime group metadata, and live hook infrastructure.

## Failure Handling
Quotacheck treats dquot verifier failures as repairable during counter reset by rereading without validation and rewriting repaired blocks. Realtime quota mounting is disabled for unsupported non-rtgroup or zoned configurations. Corrupt quota inode fields, missing metadir inodes, failed dquot flushes, and failed inode scans can disable quotas and mark the filesystem quota health state sick.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm.h

## Purpose
Defines quota manager in-core state, default quota limit structures, quota transaction accounting layout, and syscall-facing quota manager prototypes.

## Main Types and Constants
`struct xfs_quotainfo` stores per-type dquot radix trees, quota inode pointers, optional quota metadir inode, dquot LRU, quotaoff serialization lock, dquot chunk geometry, default user/group/project limits, shrinker pointer, expiry timestamp range, and live repair hook lists.

`struct xfs_def_quota` groups default block, inode, and realtime-block hard/soft limits plus grace period lengths. `struct xfs_dquot_acct` stores transaction-local dquot deltas for user, group, and project quotas, with `XFS_QM_TRANS_MAXDQS` entries per type.

## Public API
Declares quota syscall helpers for quotaon/off, quota file truncation, getquota/getquota_next, and setqlim. It also declares transaction dquot mutation helpers, quota inode loading, quotainfo destruction, and default quota lookup helpers.

## Invariants
`XFS_IS_DQUOT_UNINITIALIZED` identifies empty dquots with no limits and no usage. `xfs_dquot_tree`, `xfs_quota_inode`, and `xfs_get_defquota` switch strictly by user/group/project dquot type and assert on invalid types.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm_bhv.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm_bhv.c

## Purpose
Provides quota behavior hooks used outside the core quota manager: quota-aware `statvfs`, mount-time quota state validation, deferred quota mounting, and metadir quota state resumption.

## Main APIs
- `xfs_qm_statvfs` constrains `kstatfs` block and inode availability to the current project quota limits for project-quota directory trees.
- `xfs_qm_newmount` reconciles requested mount quota flags with on-disk quota flags and decides whether quotas can be mounted immediately or must be delayed until log recovery finishes.
- `xfs_qm_resume_quotaon` restores quota accounting/enforcement from the superblock for metadir filesystems when no explicit mount quota options were supplied.

## Key Behavior
Project quota statvfs picks data or realtime block resources according to the inode’s realtime inheritance/realtime state and clamps filesystem totals/free counts to soft limits, falling back to hard limits.

Mount validation prevents quota state changes on read-only or norecovery mounts because changing quota state would require superblock transactions. If quota accounting is already consistent and no quotacheck is needed, quotas are mounted immediately; otherwise quota flags are saved and temporarily cleared until the filesystem is ready.

## Dependencies
Uses dquot lookup/release, project id from inodes, VFS `kstatfs`, superblock quota flags, mount quota flags, readonly/norecovery checks, and metadir feature detection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm_bhv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm_syscalls.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm_syscalls.c

## Purpose
Implements the quota manager syscall backend for enabling/disabling enforcement, truncating quota files, setting quota limits/timers, and retrieving quota usage.

## Main APIs
- `xfs_qm_scall_quotaon` enables quota enforcement bits after verifying accounting is enabled.
- `xfs_qm_scall_quotaoff` disables enforcement bits; accounting shutdown is no longer supported and is ignored with an informational message.
- `xfs_qm_scall_trunc_qfiles` truncates selected quota metadata files when quotas are off.
- `xfs_qm_scall_setqlim` updates quota hard/soft limits, grace timers, id-0 default limits, preallocation limits, and dirty/log state.
- `xfs_qm_scall_getquota` returns quota usage/limits for one id, including default limits for missing non-root dquots.
- `xfs_qm_scall_getquota_next` returns the next initialized dquot at or after a requested id.

## Key Behavior
Quota enforcement changes update superblock quota flags and synchronize the superblock. Runtime in-core enforcement is changed only when accounting is already active in core. Truncation loads the quota inode, truncates extents in a transaction, updates size and timestamps, and releases the inode.

Set-limit operations validate field masks, allocate/load the dquot, join it to a transaction, apply block/realtime/inode limits independently, update id-0 defaults when modifying the root dquot, convert byte limits to filesystem blocks, and use timeout helpers to distinguish default grace periods from per-id expiry timestamps.

Getquota pushes inodegc at the start of scans so pending inode cleanup is reflected. Missing dquots with configured default limits are reported as zero-usage dquots for non-root ids. Timers are hidden from userspace when enforcement is disabled even though XFS keeps them internally.

## Dependencies
Uses quota dquot lookup, transaction reservations, quota inode loading/truncation, superblock sync, VFS `qc_dqblk` masks, inodegc push, limit/timer conversion helpers, and dquot preallocation watermark recalculation.

## Failure Handling
Invalid masks, zero enable flags, enforcement without accounting, read-only superblocks through callers, inconsistent quota state, allocation failures, and missing dquots return standard negative errno values. `-EEXIST` is intentionally used for already-off/already-on cases expected by quota utilities.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_qm_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_quota.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_quota.h

## Purpose
Declares kernel-only quota integration APIs and transaction quota accounting structures, with no-op stubs when `CONFIG_XFS_QUOTA` is disabled.

## Main Types and Macros
`XFS_NOT_DQATTACHED` detects whether an inode is missing any dquot required by currently enabled quota accounting. `XFS_QM_NEED_QUOTACHECK` determines whether enabled quota types lack checked flags in the superblock.

`struct xfs_dqtrx` tracks per-transaction quota reservations and deltas for data blocks, delayed blocks, realtime blocks, delayed realtime blocks, and inode counts. `struct xfs_apply_dqtrx_params` describes hook metadata for applying transaction quota deltas.

## Public API
When quota support is enabled, the header declares transaction dquot accounting, quota reservation, inode dquot attach/detach, create/chown/rename quota helpers, statvfs quota adjustment, mount/unmount quota hooks, enforcement-boundary checks, block reservation helpers, and optional live hook registration.

## Configuration Behavior
Without `CONFIG_XFS_QUOTA`, quota operations compile to no-ops or success-returning stubs so callers can be written unconditionally. Live hook helpers similarly become no-ops when live hooks are not built.

## Dependencies
Exposes contracts between transaction code, inode operations, mount code, dquot internals, quotactl handling, and optional online repair/live hook code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_quotaops.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_quotaops.c

## Purpose
Adapts XFS quota manager syscalls to the VFS `quotactl_ops` interface.

## Main APIs
Defines `xfs_quotactl_operations` with handlers for quota state reporting, quota timer setting, quota enable/disable, quota file removal, get/set dquot blocks, and get-next dquot scanning.

## Key Behavior
`xfs_fs_get_quota_state` reports in-core dquot count, accounting/enforcement flags, quota inode numbers, quota file block/extent counts, and default grace periods for user/group/project quota types. `xfs_qm_fill_state` loads each quota inode temporarily to fill per-type state.

VFS quota type ids are translated to XFS dquot types by `xfs_quota_type`. Userspace quota flags are translated to XFS accounting/enforcement bits by `xfs_quota_flags`.

`xfs_fs_set_info` supports timer fields only and implements them by setting id-0 quota limits through `xfs_qm_scall_setqlim`. Get/set dquot handlers translate `kqid` ids through user namespaces and dispatch to quota manager get/set helpers.

Quota file removal is allowed only when quotas are off and maps user/group/project flags to quota metadata file truncation.

## Dependencies
Uses VFS quotactl structs, superblock readonly checks, XFS mount quota flags, quota manager syscall helpers, quota inode loading, and current/init user namespace id conversion.

## Failure Handling
Read-only filesystems return `-EROFS`; disabled quota state returns `-ENOSYS`; invalid flag or field masks return `-EINVAL`. Quota file removal refuses to run while quotas are active.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_quotaops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.c

## Purpose
Implements XFS refcount btree deferred operation log items: CUI intent items and CUD done items for data and realtime refcount updates, including formatting, lifecycle, recovery, relogging, and defer-op integration.

## Main APIs
- `xfs_refcount_defer_add` queues a refcount intent onto the correct data or realtime defer type.
- `xfs_cui_log_space` and `xfs_cud_log_space` compute log space for intent/done items.
- `xfs_refcount_update_defer_type` and `xfs_rtrefcount_update_defer_type` provide deferred operation callbacks.
- `xlog_cui_item_ops`, `xlog_cud_item_ops`, `xlog_rtcui_item_ops`, and `xlog_rtcud_item_ops` register log recovery handlers.

## Key Behavior
CUI items record one or more physical extents plus operation flags for increase, decrease, CoW allocation, or CoW free. CUD items refer back to a CUI by id and release the intent when the corresponding updates have completed.

CUI lifetime uses a two-reference model so both log unpin and CUD processing can race safely with AIL insertion. Large CUI items are heap allocated; small items use a slab cache. CUD items are released when committed and drop their referenced CUI.

Deferred refcount work sorts by allocation group or realtime group, logs intents, creates done items, calls `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`, and requeues partially finished increase/decrease operations with `-EAGAIN`.

Recovery validates reflink feature availability, extent flags, operation types, and data/realtime extent ranges before reconstructing deferred work. Recovery allocates an itruncate-style reservation sized for refcount btree splits, finishes recovered intents, captures remaining defer work, and treats malformed intents as corruption.

Relogging copies extent arrays into a new CUI to push the log tail forward. Realtime CUI/CUD recovery is compiled only with `CONFIG_XFS_RT`; without it, realtime refcount intent records are reported as corruption.

## Dependencies
Uses XFS log item operations, AIL, deferred operation framework, refcount btree finish/recovery helpers, transaction reservation recovery helpers, group intent references, realtime group support, tracepoints, and slab caches.

## Failure Handling
Malformed log vectors, invalid flags, unsupported reflink state, invalid extents, or realtime intents without realtime support return `-EFSCORRUPTED`. Finish cleanup deletes btree cursors and releases AG buffers on error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.h

## Purpose
Declares in-core CUI/CUD log item structures and public helpers for deferred refcount btree updates.

## Main Types
`struct xfs_cui_log_item` embeds a log item, reference count, next-extent counter, and variable-sized CUI log format. `struct xfs_cud_log_item` embeds a log item, points to the associated CUI, and stores the CUD log format.

## Constants and API
`XFS_CUI_MAX_FAST_EXTENTS` sets the small-object slab threshold at 16 extents. The header declares CUI/CUD slab caches, `xfs_refcount_defer_add`, and log-space calculators for intent and done items.

## Semantics
The header documents the redo protocol: CUI intent items are logged in the first transaction of a rolled series, CUD done items are logged with the metadata updates, and recovery replays unfinished refcount updates after a crash.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_refcount_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.c

## Purpose
Implements XFS reflink and copy-on-write behavior: shared extent detection, CoW fork allocation/conversion/cancellation, CoW completion remapping, leftover CoW recovery, range clone/remap, unshare, reflink flag maintenance, and realtime reflink constraints.

## Main APIs
- `xfs_reflink_trim_around_shared` and `xfs_bmap_trim_cow` split file mappings at shared/unshared boundaries.
- `xfs_reflink_allocate_cow` allocates or reuses CoW fork staging blocks for writes to shared extents.
- `xfs_reflink_convert_cow` and `xfs_reflink_convert_cow_locked` convert unwritten CoW extents to written extents.
- `xfs_reflink_cancel_cow_blocks` and `xfs_reflink_cancel_cow_range` remove CoW fork reservations or real staging extents.
- `xfs_reflink_end_cow` and `xfs_reflink_end_atomic_cow` remap completed CoW data into the data fork.
- `xfs_reflink_recover_cow` frees orphaned CoW staging extents from refcount metadata during recovery.
- `xfs_reflink_remap_prep`, `xfs_reflink_remap_blocks`, and `xfs_reflink_update_dest` implement range cloning.
- `xfs_reflink_inode_has_shared_extents`, `xfs_reflink_clear_inode_flag`, and `xfs_reflink_unshare` maintain or remove the inode reflink flag.

## Key Behavior
Shared extent detection queries data-device refcount btrees or realtime refcount btrees and returns the first shared run inside a mapping. Write paths use this to trim mappings so unshared and shared regions can be processed separately. Always-CoW inodes force real extents to be treated as shared.

CoW allocation first checks for an existing overlapping CoW fork mapping. It reuses real or delalloc CoW fork extents when possible, otherwise allocates unwritten staging extents using write transactions and the inode’s CoW extent size hint. Direct I/O can request immediate conversion to written extents; buffered writes leave staging extents unwritten until writeback.

CoW cancellation walks the CoW fork backwards over a range, deletes delayed reservations, frees unwritten or requested real staging extents, removes CoW orphan records, frees physical blocks, rolls transactions through deferred work, unreserves quota, and clears the cowblocks tag when the fork is empty.

CoW completion unmaps the old data fork extent, decrements its refcount, removes delalloc reservations if present, frees the CoW orphan record, maps the written CoW extent into the data fork, adjusts quota from delayed to real blocks, deletes the CoW fork mapping, and advances through the completed I/O range. Atomic CoW reserves enough btree split space to remap the full range in one transaction.

Range clone preparation locks both files against I/O and mmap faults, rejects incompatible realtime/DAX combinations, runs generic or DAX remap prep, attaches destination dquots, zeros destination post-EOF preallocation gaps, sets reflink flags, flushes/unmaps destination cache, and leaves locks arranged for remap. Remap loops source extents, rejects unexpected delalloc, unmaps destination extents, increments source block refcounts, maps written source extents into destination, updates destination size, and reports partial progress.

Reflink flag clearing scans all written data fork extents for shared blocks and cancels leftover CoW blocks before clearing the inode flag. Unshare drives iomap or DAX writeback over a range, waits for writeback, then attempts to clear the reflink flag.

## Dependencies
Uses XFS bmap, refcount, realtime refcount, transaction, quota, iomap, DAX, page cache, inode locking, AG/rtgroup metadata, btree cursor, free-space reservation, health marking, and generic remap helpers.

## Failure Handling
Detects and marks data fork corruption for impossible same-block/different-state mappings or unexpected delalloc source extents. Low rmapbt/metafile reservations can reject reflink with `-ENOSPC`. Realtime reflink requires rtgroups and realtime extent size of one filesystem block.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.h

## Purpose
Declares reflink/CoW public helpers used by XFS write, remap, truncate, recovery, and allocation paths.

## Main API
Exports shared extent trimming, CoW allocation/conversion/cancellation/completion, atomic CoW completion, CoW recovery, remap prep/remap/update helpers, reflink flag scanning/clearing, unshare, realtime extent-size support checking, and maximum software atomic CoW sizing.

## Key Inline
`xfs_can_free_cowblocks` checks page-cache dirty/writeback tags and direct-I/O count to decide whether it is safe to free CoW fork blocks. This prevents freeing staging extents while dirty cache or in-flight I/O could still target them.

## Integration
The header forms the public boundary between reflink internals and bmap/iomap/writeback/remap/truncate code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.c

## Purpose
Implements XFS reverse-mapping btree deferred operation log items: RUI intent items and RUD done items for data and realtime rmap updates, including logging, recovery, relogging, and deferred operation callbacks.

## Main APIs
- `xfs_rmap_defer_add` queues an rmap update intent for data or realtime metadata.
- `xfs_rui_log_space` and `xfs_rud_log_space` calculate log space for intent/done records.
- `xfs_rmap_update_defer_type` and `xfs_rtrmap_update_defer_type` define defer-op behavior.
- `xlog_rui_item_ops`, `xlog_rud_item_ops`, `xlog_rtrui_item_ops`, and `xlog_rtrud_item_ops` register recovery handlers.

## Key Behavior
RUI items log owner, physical start, file offset, length, fork/state flags, and operation type for map, shared map, unmap, shared unmap, convert, shared convert, alloc, or free. RUD items refer to a prior RUI by id and cancel the outstanding intent once the corresponding rmapbt update commits.

RUI lifetime mirrors other intent items with a two-reference model for log unpin and done-item processing. Small RUI records use slab caches, larger variable-sized records use heap allocation. RUD items release their referenced RUI when committed or aborted.

Deferred rmap work sorts intents by group, logs all map records into one intent item, creates done items, calls `xfs_rmap_finish_one`, and frees intent records after processing. Realtime rmap updates use a separate defer type so realtime metadata locking does not mix with AGF locking for data-section updates.

Recovery validates rmapbt feature availability, flags, operation type, owner inode validity, file offset/length validity, and data/realtime physical extent validity. It reconstructs `xfs_rmap_intent` items from log records, allocates recovery transactions sized for rmap btree updates, finishes intents, and captures remaining defer operations.

Relogging copies the logged map extent array into a fresh RUI to move the log tail. Realtime recovery is available only with `CONFIG_XFS_RT`; otherwise realtime RUI/RUD items are corruption.

## Dependencies
Uses log item operations, AIL, deferred operation framework, rmap btree finish helpers, recovery transaction reservations, group intent references, realtime group support, tracepoints, and slab caches.

## Failure Handling
Invalid log vector sizes, malformed flags, invalid owners, invalid extents, disabled rmapbt, or unsupported realtime recovery return `-EFSCORRUPTED`. Cursor cleanup releases AG buffers on failed data-rmap operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.h

## Purpose
Declares in-core RUI/RUD log item structures and public helpers for deferred reverse-mapping btree updates.

## Main Types
`struct xfs_rui_log_item` embeds the common log item, a reference counter, next-extent counter, and variable-sized RUI log format. `struct xfs_rud_log_item` embeds a log item, references the associated RUI, and stores the RUD log format.

## Constants and API
`XFS_RUI_MAX_FAST_EXTENTS` sets the small-object slab threshold at 16 extents. The header declares RUI/RUD slab caches, `xfs_rmap_defer_add`, and log-space calculators.

## Semantics
The header documents the redo protocol for rmap updates across rolled transactions: log RUI intents first, log RUD done records with completed metadata updates, and replay unfinished rmapbt work during recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rmap_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.c

## Purpose
Implements XFS realtime volume allocation, realtime growfs, realtime mount/unmount initialization, realtime free-extent counter rebuild, and bmap integration for realtime data allocation.

## Main APIs
- `xfs_bmap_rtalloc` is the bmap allocator entry point for realtime inodes.
- `xfs_rtallocate_rtgs` allocates realtime extents across rtgroups using a rotating starting group or block hint.
- `xfs_growfs_rt` grows the realtime device and updates bitmap, summary, rtgroup, rtsb, and superblock metadata.
- `xfs_growfs_check_rtgeom` validates proposed realtime geometry and log-space feasibility.
- `xfs_rtmount_readsb`, `xfs_rtmount_freesb`, `xfs_rtmount_init`, `xfs_rtmount_inodes`, and `xfs_rtunmount_inodes` manage realtime mount metadata.
- `xfs_rtalloc_reinit_frextents` recomputes free realtime extent counters from bitmap contents.

## Key Behavior
Realtime allocation uses bitmap and summary metadata to find extents by exact start, near a hint, or by size. Summary lookups can be accelerated by an rtgroup summary cache recording the highest useful level per bitmap block. Allocation updates summary counts for the old free extent and any pre/post free fragments, then marks the allocated bitmap range.

Allocation length and placement honor realtime extent size, extent size hints, CoW extent hints for CoW fork allocation, product alignment, request min/max bounds, and end-of-volume clamping. If alignment-driven allocation fails, `xfs_bmap_rtalloc` retries with the original request and no hint alignment. Pre-rtgroup filesystems can use the bitmap inode atime as a spreading sequence for first allocations in new realtime files.

Rtgroup allocation iterates groups from a hinted group or rotor, locks bitmap metadata, searches near or by size, adjusts for busy extents on rtgroup-enabled filesystems by trimming or flushing/waiting, joins the rtgroup to the transaction, updates the bitmap/summary, decrements free realtime counters, and returns a filesystem block and length.

Growfs uses a fake mount with proposed geometry to compute derived fields and transaction reservations. It initializes or extends rt bitmap and summary files, copies summary data when summary geometry changes, writes the realtime superblock when adding an rtsb-backed realtime volume, initializes rtrmap state for the rtsb, frees newly added realtime extents into the bitmap, updates superblock fields and free counters, recalculates rsum values and btree maxlevels, and updates secondary superblocks plus metafile reservations.

Rtgroup grow supports extending the last partial group and allocating new rtgroups. Zoned realtime grow follows a separate path that updates superblock geometry and makes new zones available instead of bitmap/summary freeing. Geometry checks reject unsupported shrink, invalid extent sizes, unsupported quota/rmap/reflink combinations on non-rtgroup filesystems, non-rtgroup reflink realtime extent sizes, excessive summary-vs-log sizing, and zoned sizes not aligned to rtgroup size.

Mount-time code reads and pins the realtime superblock when present, verifies realtime device availability and size, computes summary blocks/levels, loads rtgroup metadata inodes, preloads their extent maps to allow shared-lock bitmap scans, and allocates summary caches except on zoned filesystems. Unmount releases per-rtgroup metadata inodes and summary caches.

## Dependencies
Uses realtime bitmap/summary helpers, rtgroup metadata and locks, rt metadata inodes, realtime superblock verifiers, transaction reservations, bmap extent-size alignment, quota reservation accounting, busy extent tracking, rtrmap and rtrefcount btree maxlevel computation, metafile reservations, zoned allocation, health/error reporting, and secondary superblock updates.

## Failure Handling
Read-only capability checks, missing rtdev, last-block read failures, invalid geometry, summary corruption, allocation exhaustion, busy extents, transaction failures, and metadata initialization failures propagate errno. Growfs attempts to keep completed rtgroup growth reflected in secondary superblocks even after partial errors and restores rtgroup geometry/summary-cache state on per-group grow failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.h

## Purpose
Declares realtime allocation, realtime mount, realtime growfs, and realtime geometry helpers.

## Main API
With `CONFIG_XFS_RT`, the header declares realtime superblock read/free, mount initialization, rt metadata inode loading/unloading, realtime growfs, free-extent counter rebuild, geometry checking, and rtgroup allocation.

`xfs_rtallocate_rtgs` remains declared outside the feature guard because allocation call sites can reference it directly when realtime support is built into the surrounding configuration.

## Configuration Behavior
Without `CONFIG_XFS_RT`, growfs returns `-ENOSYS`, free-counter rebuild and rtsb read are no-ops, mount initialization permits filesystems without realtime blocks and rejects realtime volumes with a warning, and geometry checking succeeds trivially.

## Dependencies
The header is the public boundary between realtime allocation internals, mount code, growfs ioctl handling, and bmap allocation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.h -->