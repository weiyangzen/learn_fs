# Group Research: group_875_linux_sources_os_linux_linux_fs_xfs_xfs_log_recover_c_sources_os_lin_7be14b6951b6

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log_recover.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_log_recover.c

## Purpose

`xfs_log_recover.c` implements XFS journal recovery. It locates the active portion of the circular on-disk log, validates record headers and CRCs, detects clean unmounts and torn writes, replays logged metadata items in ordered passes, processes recovered deferred intent work, rebuilds unlinked inode state, and finalizes recovery before normal filesystem operation resumes.

## Main Responsibilities

- Perform sector-aligned log I/O through `xlog_bread`, `xlog_bwrite`, and `xlog_do_io`.
- Find the log head and tail using cycle numbers, log record headers, and zeroed-log detection.
- Validate log record headers against log format, UUID, version, length, and CRC expectations.
- Detect and trim torn writes near the log head via CRC verification.
- Clear stale blocks beyond the discovered head so later crashes do not misidentify partial writes as valid records.
- Replay log transactions in two passes:
  - pass 1 gathers cancellation information, especially cancelled buffer items.
  - pass 2 replays buffers, inodes, dquots, quotaoff records, inode creation records, and intent/done item families.
- Reorder recovered transaction items to satisfy inode allocation, inode item, inode unlink buffer, and cancellation dependencies.
- Reconstruct transaction state from log operation headers, including split and continued regions.
- Process recovered intent items through deferred operation recovery.
- Recover AGI unlinked inode lists and leftover CoW staging extents after primary replay.
- Re-read and reinitialize the superblock after log replay.

## Key Data Flow

Recovery starts in `xlog_recover`. It calls `xlog_find_tail` to determine `head_blk` and `tail_blk`. If the log is dirty and recovery is allowed, it calls `xlog_do_recover`.

`xlog_do_recover` calls `xlog_do_log_recovery`, which allocates the buffer-cancel table and runs `xlog_do_recovery_pass` twice. After replay, it assigns the AIL tail, rereads the primary superblock buffer, refreshes in-core superblock features and counters, and clears active recovery state.

The second-stage public entrypoint is `xlog_recover_finish`. It runs recovered intents, forces the log, processes unlinked inode lists, and recovers leftover CoW staging extents. `xlog_recover_cancel` cancels pending recovered intents if mount recovery is abandoned.

## Important Functions

- `xlog_verify_bno`: bounds-checks log-relative block ranges.
- `xlog_alloc_buffer`: allocates log-sector-sized buffers, with extra space for unaligned sector handling.
- `xlog_header_check_recover`: rejects dirty logs with incompatible format or mismatched filesystem UUID.
- `xlog_header_check_mount`: validates mount-time log headers, tolerating old IRIX-style null UUID logs.
- `xlog_find_zeroed`: detects totally or partially zeroed logs and finds the first zero-cycle block.
- `xlog_find_head`: finds the next log write position, accounting for wraparound, incomplete writes, and partial records.
- `xlog_verify_head`: CRC-checks the possible in-flight log records near the head and trims torn writes.
- `xlog_verify_tail`: validates the tail and can advance it past overwritten tail records near the head.
- `xlog_clear_stale_blocks`: overwrites possible stale future-head blocks with empty records.
- `xlog_recover_reorder_trans`: sorts transaction items into replay-safe order.
- `xlog_recover_commit_trans`: commits a recovered transaction for a recovery pass.
- `xlog_recover_add_to_trans` and `xlog_recover_add_to_cont_trans`: assemble recovered log item regions, including split transaction headers and continued regions.
- `xlog_recover_process_ophdr`: validates operation headers, maps them to recovered transaction objects, and drains delayed-write buffers when recovery LSN changes.
- `xlog_recover_process`: CRC-checks, unpacks cycle data, and dispatches log record payload processing.
- `xlog_do_recovery_pass`: walks from tail to head, including physical-log wrap cases, and processes records.
- `xlog_recover_process_intents`: finishes recovered deferred intent work in log order.
- `xlog_recover_process_iunlinks`: scans AGI unlinked buckets and drives inodegc to finish deletion.
- `xlog_recover_iget` and `xlog_recover_iget_handle`: retrieve inodes for recovery, attach dquots, and validate inode generation when required.

## Recovery Ordering

The file explicitly documents and enforces replay order because metadata dependencies matter:

1. Non-cancelled buffers are replayed before most items.
2. Non-buffer items are replayed next.
3. Inode unlink buffers are replayed after inode items.
4. Cancelled buffers are processed last.

This avoids replaying stale cancelled buffers too early and ensures inode allocation/unlink dependencies are respected.

## Error Handling and Corruption Policy

The implementation treats unexpected log format, UUID mismatch, bad record lengths, invalid log block ranges, unknown operation clients, bad transaction headers, and unsupported log incompat bits as corruption or invalid recovery conditions. CRC mismatch is advisory for old non-CRC filesystems but fatal for CRC-enabled filesystems. I/O errors are surfaced unless the log is already shut down.

If recovery of intents fails, the code cancels pending intents, emits an alert, and shuts down the log. For CoW staging recovery failure, it forces shutdown but returns zero so already committed log items can be pushed through CIL/AIL.

## External Dependencies

This file depends heavily on XFS log internals, transaction item ops, buffer recovery, inode recovery, quota recovery, deferred ops, AIL, per-AG iteration, inodegc, and reflink recovery. It includes item ops for buffer, inode, dquot, quotaoff, icreate, EFI/EFD, RUI/RUD, CUI/CUD, BUI/BUD, ATTRI/ATTRD, XMI/XMD, and realtime intent families.

## Notable Edge Cases

- Totally zeroed logs are warned about because Linux XFS normally writes a dummy unmount record.
- Variable-length v2 log headers are supported, including compatibility handling for a known xfsprogs header-size bug.
- Log records and headers can wrap around the end of the physical circular log.
- Torn writes are tolerated only within the policy window of possible in-flight iclogs.
- Recovery can run on read-only mounts, but not on read-only underlying devices.
- Unknown v5 incompatible log features block recovery before any modification.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_message.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_message.c

## Purpose

`xfs_message.c` implements XFS logging and assertion-message helpers. It centralizes printk formatting for mount-aware XFS messages, panic-mask alert escalation, assertion handling, hex dumps, buffer-specific rate-limited alerts, and experimental-feature warnings.

## Main Responsibilities

- Format messages as `XFS (<sb id>): ...` when a mount and superblock are available.
- Emit generic `XFS: ...` messages when no mount context exists.
- Trigger stack traces for high error verbosity on error-or-worse log levels.
- Convert selected alert tags into `BUG()` paths via `xfs_panic_mask`.
- Provide `asswarn` and `assfail` backends for XFS assertions.
- Provide `xfs_hex_dump`.
- Rate-limit buffer alerts using the buffer target’s I/O error ratelimit state.
- Warn once per mount for experimental features.

## Important Functions

- `__xfs_printk`: private formatter that chooses mount-specific or generic prefix.
- `xfs_printk_level`: varargs printk wrapper used by severity macros in `xfs_message.h`.
- `_xfs_alert_tag`: alert wrapper that can transform configured panic tags into `BUG_ON`.
- `asswarn`: warning assertion backend using `xfs_warn` and `WARN_ON`.
- `assfail`: fatal assertion backend using `xfs_emerg` and either `BUG()` or `WARN_ON`, depending on `xfs_globals.bug_on_assert`.
- `xfs_buf_alert_ratelimited`: emits buffer-target rate-limited alerts.
- `xfs_warn_experimental`: warns once for online shrink, logged extended attributes, or zoned RT device experimental features.

## External Dependencies

The file uses `xfs_mount`, `xfs_error_level`, `xfs_panic_mask`, `xfs_globals`, mount opstate warning bits, kernel printk, rate limiting, and hex dump facilities.

## Notes

The implementation intentionally keeps severity-specific public interfaces in the header as macros while centralizing varargs handling and mount-prefix formatting here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_message.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_message.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_message.h

## Purpose

`xfs_message.h` declares XFS message and assertion interfaces and defines the severity macros used throughout XFS.

## Main Responsibilities

- Define `xfs_emerg`, `xfs_alert`, `xfs_crit`, `xfs_err`, `xfs_warn`, `xfs_notice`, `xfs_info`, and debug variants.
- Integrate printk indexing through `printk_index_subsys_emit`.
- Provide rate-limited and once-only wrappers around the severity macros.
- Declare assertion handlers, hex dump support, buffer-alert support, and experimental feature warning support.

## Important Interfaces

- `xfs_printk_level`: severity-level backend.
- `xfs_alert_tag`: indexed alert wrapper that calls `_xfs_alert_tag`.
- `xfs_printk_ratelimited`: local static ratelimit wrapper macro.
- `xfs_printk_once`: `DO_ONCE_LITE` wrapper.
- `assfail` and `asswarn`: assertion backends used by `xfs_platform.h`.
- `xfs_buf_alert_ratelimited`: per-buffer-target alert path.
- `enum xfs_experimental_feat`: enumerates experimental feature warnings.

## Conditional Behavior

`xfs_debug` emits only in `DEBUG` builds. In non-debug builds, it compiles to an empty statement. `xfs_debug_ratelimited` still resolves through the debug macro and therefore inherits that behavior.

## Dependencies

Includes `linux/once_lite.h` and forward-declares `struct xfs_mount`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_message.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mount.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_mount.c

## Purpose

`xfs_mount.c` implements core XFS mount and unmount lifecycle logic, superblock reading, UUID uniqueness, geometry setup, free-space accounting, log feature flag updates, reserve-pool handling, and delayed allocation accounting.

## Main Responsibilities

- Maintain a global mounted-filesystem UUID table.
- Read and validate the primary superblock.
- Initialize mount geometry, feature state, directory/attribute geometry, realtime metadata, per-AG and rtgroup state, quota state, log state, and work queues.
- Perform mount-time recovery sequencing in cooperation with the log code.
- Tear down mounted filesystems cleanly during unmount or failed mount.
- Manage free block and realtime extent counters with reserve pools.
- Validate and configure stripe alignment, allocation size, low-space thresholds, and atomic write limits.
- Add and clear log incompat feature bits safely.
- Track delayed allocation blocks and realtime extents.

## Key Mount Flow

`xfs_mountfs` is the main mount function. It:

1. Initializes common superblock-derived mount state.
2. Corrects legacy mismatched `features2` state if necessary.
3. Ensures v2 inode/link-count feature state.
4. Validates and applies stripe alignment options.
5. Computes btree and inode geometry.
6. Initializes sysfs, scrub stats, error tags, and UUID registration.
7. Validates sparse inode alignment and device sizes.
8. Initializes realtime mount fields and directory/attribute geometry.
9. Initializes transaction reservations, per-AG state, and rtgroups.
10. Registers inodegc shrinker.
11. Mounts the log and performs the first recovery phase.
12. Starts inodegc and blockgc.
13. Loads metadata directory, root inode, and realtime inodes.
14. Checks summary counters.
15. Syncs superblock updates if needed and writable.
16. Initializes quota management.
17. Finishes log recovery after root/realtime metadata is available.
18. Cleans log for read-only recovered mounts.
19. Mounts zoned state if enabled.
20. Reserves free-space pools and AG metadata space.
21. Computes atomic write unit maxima.

The error path unwinds each stage in reverse order, including inode release, quota cleanup, inodegc flushing, log cancellation, buftarg draining, group freeing, UUID removal, sysfs cleanup, and scrub stats unregistering.

## Key Unmount Flow

`xfs_unmountfs`:

- Flushes inodegc.
- Stops blockgc and zone gc.
- Releases AG reservations and quota state.
- Unmounts zoned, realtime, root, and metadata directory inodes.
- Flushes inodes and AIL through `xfs_unmount_flush_inodes`.
- Unmounts quota internals.
- Releases reserved block pools.
- Checks free inode counters.
- Marks log incompat bits clearable and unmounts the log.
- Frees DA geometry, UUID table entry, shrinker, rtgroups, per-AG state, error tags, scrub stats, and sysfs state.

## Important Functions

- `xfs_uuid_mount` / `xfs_uuid_unmount`: enforce unique non-null UUIDs unless `nouuid` is set.
- `xfs_readsb`: reads the superblock first with device sector size, then rereads with filesystem sector size and verifiers.
- `xfs_validate_new_dalign`: validates mount-option stripe unit/width and converts them to fsblocks.
- `xfs_update_alignment`: applies stripe alignment changes or reads existing superblock alignment.
- `xfs_set_low_space_thresholds`: computes 1%-5% free-space thresholds for speculative preallocation.
- `xfs_check_sizes`: verifies readable last sector of data and external log devices.
- `xfs_mount_reset_sbqflags`: clears quota flags in-core and on disk when needed.
- `xfs_default_resblks`: computes default reserve pools.
- `xfs_check_summary_counts`: validates or recomputes summary counters after log recovery.
- `xfs_unmount_flush_inodes`: forces log, waits for busy extents/discards, stops inodegc, pushes AIL, reclaims inodes, and unmounts health state.
- `xfs_set_max_atomic_write_opt`: validates user-requested max atomic write size and computes reservation support.
- `xfs_fs_writable`: checks freeze level, shutdown, and readonly state.
- `xfs_add_freecounter` / `xfs_dec_freecounter`: update free counters and reserve pools.
- `xfs_add_incompat_log_feature`: safely writes log incompat bits to the primary superblock before later log items require them.
- `xfs_clear_incompat_log_features`: clears log incompat flags when safe.
- `xfs_mod_delalloc`: updates delayed allocation counters for data or realtime inodes.

## Free-Space Accounting

The file uses percpu counters for free blocks, free realtime extents, available realtime extents, allocated/free inode counts, and delayed allocation counts. `xfs_dec_freecounter` uses large batches under normal conditions but switches to accurate accounting near ENOSPC. Reserved pools can be consumed only by callers passing `rsvd`.

## Atomic Write Handling

Atomic write maximums are constrained by:

- kernel maximum write size,
- reflink CoW completion limits,
- group size and group alignment,
- hardware atomic-write support,
- filesystem block alignment,
- transaction reservation feasibility.

The computed per-group maxima are stored in `m_groups[type].awu_max`.

## Error Handling

Mount initialization has extensive staged unwind labels. Metadata corruption uses `XFS_IS_CORRUPT` where applicable. Read-only devices reject operations requiring write access, such as recovery. Mount can continue without reserve pools in some ENOSPC cases but fails on structural or recovery errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mount.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_mount.h

## Purpose

`xfs_mount.h` defines the central `struct xfs_mount`, mount feature flags, operational state bits, free counter helpers, shutdown flags, mount lifecycle prototypes, and mount-level utility interfaces.

## Main Structures

- `struct xfs_error_cfg`: sysfs-backed retry configuration for metadata error handling.
- `struct xfs_inodegc`: per-cpu deferred inode inactivation list and work state.
- `struct xfs_groups`: geometry container for allocation groups and realtime groups.
- `struct xfs_freecounter`: percpu free counter plus reserve pool accounting.
- `struct xfs_mount`: the main in-core filesystem mount object.

## `struct xfs_mount` Contents

The mount object stores:

- In-core superblock and Linux superblock pointer.
- AIL, log, primary and realtime superblock buffers.
- Root, metadata directory, realtime directory, quota, device target, and filestream references.
- Workqueues for buffer, unwritten extent, reclaim, sync, blockgc, and inodegc work.
- Precomputed block, inode, btree, realtime, directory, transaction, and allocation geometry.
- Feature and opstate bitmasks.
- Health, sickness, checked-state, scrub, sysfs, debugfs, errortag, and stats state.
- Per-cpu counters and reserve pools.
- Data and realtime group geometry.
- Inodegc shrinker, delayed work, growfs generation/lock, hook lists, health monitor pointer, and UUID table index.

The layout intentionally places read-mostly fields before frequently modified counters and locks.

## Feature Flags

`XFS_FEAT_*` bits describe active filesystem and mount features, including attrs, quotas, CRCs, rmapbt, reflink, sparse inodes, metadir, zoned realtime, DAX policy, filestreams, no-recovery, and nouuid.

The header generates feature helpers with macros such as:

- `xfs_has_reflink`
- `xfs_has_rmapbt`
- `xfs_has_metadir`
- `xfs_has_zoned`
- `xfs_has_norecovery`
- `xfs_has_nouuid`

Some features also have `xfs_add_*` helpers that update both in-core features and superblock version state.

## Operational State

`XFS_OPSTATE_*` bits represent dynamic mount state:

- unmounting,
- clean,
- shutdown,
- inode32,
- readonly,
- inodegc/blockgc enabled,
- one-time experimental warnings,
- quotacheck/resuming quotaon,
- log incompat cleanup state,
- logged xattrs enabled,
- zonegc running.

The header generates `xfs_is_*`, `xfs_set_*`, and `xfs_clear_*` helpers for these bits.

## Shutdown Flags

Defines `SHUTDOWN_META_IO_ERROR`, `SHUTDOWN_LOG_IO_ERROR`, `SHUTDOWN_FORCE_UMOUNT`, `SHUTDOWN_CORRUPT_INCORE`, `SHUTDOWN_CORRUPT_ONDISK`, and `SHUTDOWN_DEVICE_REMOVED`, plus string mappings for tracing/reporting.

## Free Counter Helpers

The header provides inline wrappers for:

- summing, estimating, comparing, and setting free counters,
- decrementing/adding data free blocks,
- decrementing/adding realtime extents,
- accounting delayed allocation blocks.

The main implementations live in `xfs_mount.c`.

## Public Interfaces

Important declarations include:

- `xfs_mountfs`, `xfs_unmountfs`
- `xfs_readsb`, `xfs_freesb`
- `xfs_fs_writable`
- `xfs_sb_validate_fsb_count`
- `xfs_default_resblks`
- `xfs_dev_is_read_only`
- `xfs_set_low_space_thresholds`
- `xfs_zero_extent`
- `xfs_error_get_cfg`
- `xfs_force_summary_recalc`
- `xfs_add_incompat_log_feature`
- `xfs_clear_incompat_log_features`
- `xfs_mod_delalloc`
- `xfs_set_max_atomic_write_opt`
- `xfs_group_type_buftarg`

## Notes

This header is a major cross-subsystem contract. Many XFS subsystems depend on it for feature predicates, mount state transitions, free-space accounting, and access to core mount geometry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mru_cache.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_mru_cache.c

## Purpose

`xfs_mru_cache.c` implements a time-bucketed most-recently-used cache for XFS clients. Elements are keyed by `unsigned long`, stored in a radix tree for lookup, and grouped into time lists for periodic expiration.

## Design

The cache uses:

- a radix tree for key-to-element lookup,
- an array of list heads representing discrete time groups,
- a reap list for expired elements,
- a spinlock protecting internal state,
- delayed work for timed reaping,
- a client-provided free callback.

Elements do not store individual expiration timestamps. Instead, the cache advances a time window and migrates old whole buckets to the reap list. This reduces per-element memory and enables grouped expiration.

## Main Functions

- `xfs_mru_cache_init`: creates the global MRU reaper workqueue.
- `xfs_mru_cache_uninit`: destroys the global workqueue.
- `xfs_mru_cache_create`: allocates and initializes a cache instance.
- `xfs_mru_cache_destroy`: flushes and frees a cache.
- `xfs_mru_cache_insert`: inserts an element into the radix tree and current MRU bucket.
- `xfs_mru_cache_remove`: removes an element without calling the free callback.
- `xfs_mru_cache_delete`: removes and frees an element.
- `xfs_mru_cache_lookup`: looks up an element, refreshes it into the current MRU bucket, and returns with the cache lock held.
- `xfs_mru_cache_done`: releases the lock after a successful lookup.

## Internal Helpers

- `_xfs_mru_cache_migrate`: advances time buckets and moves expired lists to the reap list.
- `_xfs_mru_cache_list_insert`: migrates buckets and inserts an element into the current bucket.
- `_xfs_mru_cache_clear_reap_list`: removes expired elements from radix tree and calls free callbacks outside the spinlock.
- `_xfs_mru_cache_reap`: delayed-work callback that migrates and frees expired elements, then reschedules itself if needed.
- `xfs_mru_cache_flush`: cancels pending work and expires all remaining elements.

## Locking Contract

`xfs_mru_cache_lookup` is unusual: on success it returns with the internal spinlock held so the caller can inspect or update the element cheaply. The caller must call `xfs_mru_cache_done`. On lookup miss, the function releases the lock before returning `NULL`.

## Error Handling

Creation validates non-null output pointer, nonzero lifetime, nonzero group count, nonzero computed group time, and non-null free callback. Insert preloads radix-tree memory and frees the element via the callback on failure.

## Notes

An extra list group is allocated to avoid reaping elements up to one group interval too early. The implementation uses `__GFP_NOFAIL` allocations for cache and list structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mru_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mru_cache.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_mru_cache.h

## Purpose

`xfs_mru_cache.h` declares the XFS MRU cache interface and the element structure embedded by clients.

## Main Definitions

- `struct xfs_mru_cache`: opaque cache handle.
- `struct xfs_mru_cache_elem`: list node plus key stored by each cached element.
- `xfs_mru_cache_free_func_t`: client callback used to free expired or failed elements.

## Public API

- global lifecycle: `xfs_mru_cache_init`, `xfs_mru_cache_uninit`
- cache lifecycle: `xfs_mru_cache_create`, `xfs_mru_cache_destroy`
- element operations: `xfs_mru_cache_insert`, `xfs_mru_cache_remove`, `xfs_mru_cache_delete`, `xfs_mru_cache_lookup`, `xfs_mru_cache_done`

## Usage Notes

Clients provide the lifetime, bucket count, opaque data pointer, and free callback at creation time. Successful lookup requires a matching `xfs_mru_cache_done` call to release the cache lock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_mru_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_notify_failure.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_notify_failure.c

## Purpose

`xfs_notify_failure.c` implements DAX media failure notification handling for XFS. It translates DAX-device failure ranges into filesystem block ranges, reports media health events, identifies affected file mappings through reverse-mapping btrees, kills affected DAX mappings/processes where appropriate, invalidates pages for pre-removal, and shuts down the filesystem when metadata or log corruption is implied.

## Main Data Structure

`struct xfs_failure_info` carries:

- group-relative start block,
- block count,
- memory failure flags,
- `want_shutdown` flag set when non-file metadata or lookup failures imply unsafe state.

## Main Functions

- `xfs_failure_pgoff`: computes file page offset for the overlap between a reverse map record and the failed range.
- `xfs_failure_pgcnt`: computes affected page count for the overlap.
- `xfs_dax_failure_fn`: rmap query callback that handles each affected extent.
- `xfs_dax_notify_failure_freeze`: freezes the filesystem under kernel holder before pre-remove handling.
- `xfs_dax_notify_failure_thaw`: thaws kernel and userspace holders after pre-remove handling.
- `xfs_dax_translate_range`: maps DAX failure offset/length to filesystem device daddr and basic-block length.
- `xfs_dax_notify_logdev_failure`: handles failure on an external log device.
- `xfs_dax_notify_dev_failure`: handles data or realtime device failures by querying rmap metadata.
- `xfs_dax_notify_failure`: dispatches failure notification based on which XFS buftarg owns the DAX device.

## Behavior

For file-owned rmap records, the callback tries to get an incore inode. If the inode is DAX-backed, it calls `mf_dax_kill_procs` for the affected file page range. For pre-remove notifications it invalidates affected page cache ranges. It always reports data loss through `fserror_report_data_lost`.

For metadata, attr fork, bmbt block, missing inode, or other unsafe cases, the code requests filesystem shutdown unless this is a pre-remove path where forced unmount is expected.

## Device Handling

- Whole-device notification is represented by `offset == 0 && len == U64_MAX`.
- Out-of-filesystem ranges return `-ENXIO`.
- Log device failure reports health and shuts down as corrupt on-disk state unless pre-remove.
- Data/realtime failure requires rmapbt; otherwise it returns `-EOPNOTSUPP`.

## Pre-Remove Handling

When `MF_MEM_PRE_REMOVE` is set, XFS logs that the device is about to be removed, attempts to freeze the filesystem to prevent new mappings, scans affected mappings, then force-shuts down with `SHUTDOWN_FORCE_UMOUNT` and thaws holders.

## Exported Interface

The file exports `xfs_dax_holder_operations` with `.notify_failure = xfs_dax_notify_failure`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_notify_failure.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_notify_failure.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_notify_failure.h

## Purpose

`xfs_notify_failure.h` declares the XFS DAX holder operations object used for media failure notification.

## Public Interface

- `extern const struct dax_holder_operations xfs_dax_holder_operations;`

## Notes

The implementation is in `xfs_notify_failure.c`. This header intentionally contains only the external declaration and include guard.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_notify_failure.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_platform.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_platform.h

## Purpose

`xfs_platform.h` is the Linux-kernel platform adaptation header for XFS. It pulls in kernel headers, defines XFS platform types and constants, maps XFS configuration options to compile-time flags, wires assertion/corruption helpers, and provides small portability wrappers.

## Main Responsibilities

- Include Linux kernel APIs needed broadly by XFS.
- Define core XFS scalar types such as `xfs_off_t`, `xfs_ino_t`, `xfs_daddr_t`, `xfs_dev_t`, and `xfs_nlink_t`.
- Include foundational XFS headers used widely across the subsystem.
- Map `CONFIG_XFS_*` options to `DEBUG`, `DEBUG_EXPENSIVE`, `XFS_ASSERT_FATAL`, and `XFS_WARN`.
- Expose sysctl parameter aliases such as `xfs_panic_mask`, `xfs_error_level`, and timer settings.
- Define block-device I/O constants and error aliases.
- Provide assertion macros and corruption-detection macro.
- Provide realtime inode/mount predicates based on `CONFIG_XFS_RT`.
- Provide pointer-format policy for debug vs non-debug builds.
- Provide `kmem_to_page` for vmalloc or direct kernel memory.

## Important Macros and Helpers

- `current_cpu`, `current_set_flags_nested`, `current_restore_flags_nested`
- `BLKDEV_IOSHIFT`, `BLKDEV_IOSIZE`, `BLKDEV_BB`
- `ENOATTR`, `EWRONGFS`
- `__this_address`: label-address helper protected by `barrier`.
- `howmany`
- `delay`: uninterruptible schedule timeout wrapper.
- `xfs_to_linux_dev_t` and `linux_to_xfs_dev_t`
- `xfs_sort`
- `xfs_stack_trace`
- `rounddown_64`, `roundup_64`, `howmany_64`, `isaligned_64`
- `log2_if_power2`, `mask64_if_power2`
- `ASSERT_ALWAYS`, `ASSERT`
- `XFS_IS_CORRUPT`
- `STATIC`: defined as `static noinline`
- `XFS_IS_REALTIME_INODE`, `XFS_IS_REALTIME_MOUNT`
- `PTR_FMT`
- `kmem_to_page`

## Assertion Behavior

In debug builds, `ASSERT` calls `assfail`. In non-debug builds with `XFS_WARN`, it calls `asswarn`; otherwise it compiles out. `ASSERT_ALWAYS` always calls `assfail` on failure.

## Dependencies

This header includes many XFS subsystem headers, including stats, sysctl, iops, aops, superblock, checksum, buffer, message, drain, and hooks headers. It is a foundational include for most XFS C files.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_platform.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pnfs.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_pnfs.c

## Purpose

`xfs_pnfs.c` implements XFS support for pNFS block layouts through `exportfs_block_ops`. It maps file byte ranges to block-device layouts for NFS clients, commits client-written blocks, and coordinates layout recalls with local filesystem operations.

## Main Responsibilities

- Break outstanding leased pNFS layouts before local operations that remove blocks.
- Advertise supported block layout ID modes.
- Export a stable filesystem UUID and its superblock offset.
- Map file ranges to iomaps for pNFS clients.
- Allocate blocks for pNFS writes and make the allocation durable before handing it out.
- Commit client-written blocks by invalidating cache, converting unwritten extents, updating timestamps, and optionally extending file size.

## Important Functions

- `xfs_break_leased_layouts`: loops on `break_layout`; if blocking is needed, drops/reacquires XFS IOLOCK exclusively and reports that it unlocked.
- `xfs_fs_layouts_supported`: advertises in-band ID support and optional out-of-band ID support from the block device.
- `xfs_fs_get_uuid`: returns the filesystem UUID and offset of `sb_uuid` in the disk superblock.
- `xfs_fs_map_update_inode`: strips SUID/SGID as needed, updates mtime/ctime, marks preallocation, logs inode core, and commits.
- `xfs_fs_map_blocks`: validates export constraints, flushes and invalidates pagecache, maps or allocates extents, logs durability, converts to iomap, and returns device generation.
- `xfs_pnfs_validate_isize`: ensures a proposed size extension lands in a valid allocated written block.
- `xfs_fs_commit_blocks`: invalidates affected cache, converts unwritten extents, updates timestamps and size, and commits synchronously.

## Export Constraints

The mapping path rejects:

- shutdown filesystems,
- realtime inodes because the realtime device lacks a UUID export identity,
- reflink inodes because Linux pNFS block layout does not implement the needed reflink semantics,
- offsets beyond allowed file size limits.

## Locking and Consistency

`xfs_fs_map_blocks` takes `XFS_IOLOCK_EXCL`, flushes dirty pagecache, invalidates cached pages, reads or allocates mappings under data-map locks, and forces the log for newly allocated write layouts. `xfs_fs_commit_blocks` also takes `XFS_IOLOCK_EXCL` while converting extents and updating inode metadata.

## Exported Interface

The file defines `xfs_export_block_ops` with:

- `.layouts_supported`
- `.get_uuid`
- `.map_blocks`
- `.commit_blocks`
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pnfs.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_pnfs.h

## Purpose

`xfs_pnfs.h` declares XFS pNFS block-layout interfaces and provides a stub for builds without block export operations.

## Public Interface

- `xfs_break_leased_layouts`: declared when `CONFIG_EXPORTFS_BLOCK_OPS` is enabled; otherwise an inline stub returns 0.
- `xfs_export_block_ops`: external exportfs block operations table.

## Dependencies

Includes `linux/exportfs_block.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pnfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pwork.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_pwork.c

## Purpose

`xfs_pwork.c` implements a small parallel workqueue abstraction for XFS tasks that can be split across CPUs. It wraps Linux workqueues with XFS-specific control state, error recording, polling support, and tracing.

## Main Responsibilities

- Initialize a workqueue for a parallel task.
- Queue embedded `struct xfs_pwork` items.
- Invoke a caller-provided work function for each item.
- Record the first nonzero worker error.
- Track outstanding work count.
- Wake pollers when all work completes.
- Destroy the workqueue and return recorded error.
- Provide polling that touches the soft lockup watchdog.

## Important Functions

- `xfs_pwork_init`: allocates an unbound, sysfs-visible, freezable workqueue named from the caller tag and current pid. In debug builds, `xfs_globals.pwork_threads` can cap parallelism.
- `xfs_pwork_queue`: initializes the work item, attaches control state, increments outstanding count, and queues work.
- `xfs_pwork_work`: internal workqueue callback that calls the client function and updates error/completion state.
- `xfs_pwork_destroy`: destroys the workqueue and returns `pctl->error`.
- `xfs_pwork_poll`: waits in one-second intervals for outstanding work to reach zero and touches the softlockup watchdog between waits.

## Concurrency Notes

`pctl->error` records the first observed worker error but does not stop already queued work. Work functions are expected to check `xfs_pwork_want_abort` or `xfs_pwork_ctl_want_abort` if they should stop early after another worker reports failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pwork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pwork.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_pwork.h

## Purpose

`xfs_pwork.h` declares the XFS parallel work abstraction.

## Main Types

- `xfs_pwork_work_fn`: callback signature taking mount and pwork item.
- `struct xfs_pwork_ctl`: owns workqueue, mount pointer, callback, waitqueue, outstanding work count, and first error.
- `struct xfs_pwork`: embeddable work item with Linux `work_struct` and backpointer to the control object.

## Public API

- `xfs_pwork_init`
- `xfs_pwork_queue`
- `xfs_pwork_destroy`
- `xfs_pwork_poll`

## Helpers

- `XFS_PWORK_SINGLE_THREADED`: initializer for non-queued single-threaded usage.
- `xfs_pwork_ctl_want_abort`: true if control object exists and has an error.
- `xfs_pwork_want_abort`: checks abort state from an embedded pwork item.

## Notes

The abstraction is intentionally thin. It does not cancel queued work on first error; it exposes the error state so workers and callers can decide how aggressively to stop.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_pwork.h -->