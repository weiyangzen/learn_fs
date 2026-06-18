# Group Research: group_1117_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_log_recover_c_adc4b64704d6

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log_recover.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log_recover.c

## Purpose
Implements XFS journal recovery: log head/tail discovery, log record validation, two-pass transaction replay, deferred intent recovery, stale log block clearing, unlinked inode cleanup, and post-recovery CoW staging cleanup.

## Main APIs
- `xlog_recover` locates active log range, validates superblock LSN/log feature compatibility, and runs first-stage replay.
- `xlog_recover_finish` completes recovered intents, processes AGI unlinked lists, and frees leftover CoW staging extents.
- `xlog_recover_cancel` cancels pending recovered intents after mount failure.
- `xlog_recover_iget` and `xlog_recover_iget_handle` acquire inodes for intent replay, with generation validation for handle-like intents.
- `xlog_recover_intent_item`, `xlog_recover_release_intent`, and `xlog_recover_finish_intent` manage recovered intent/done item lifecycle.
- `xlog_buf_readahead` issues metadata readahead unless the buffer was canceled.

## Log Discovery
Recovery reads the circular physical log in sector-aligned units, validates log-relative block ranges, and handles logical offsets inside sector-sized buffers. Head discovery scans cycle numbers, detects zeroed logs, backs up over partial log records, and checks record headers. Tail discovery uses the last good record’s tail LSN, detects clean unmount records, initializes in-core log state, and clears stale blocks ahead of the head when the device is writable.

## CRC and Torn Write Handling
The code verifies candidate records with log CRCs. CRC failures within the possible in-flight iclog window are treated as torn writes: recovery truncates the head to the first bad record, backs up to the last good record, and revalidates the tail. Tail verification can advance past overwritten records close to the head, but reports corruption when bad records fall outside the safe overwrite window.

## Replay Pipeline
Recovery registers per-item operations for buffer, inode, dquot, quotaoff, icreate, extent-free, rmap, refcount, bmap, attr, exchange-range, and realtime intent/done items. Pass 1 records canceled buffers; pass 2 replays live items. Operation headers rebuild transactions, including split/continued regions. Transactions are reordered so ordinary buffers replay before non-buffer items, inode-unlink buffers replay late, and canceled buffers replay last.

## Ordering and Failure Handling
Recovered dirty buffers are submitted only when the recovery LSN changes, preventing metadata LSN updates from causing same-LSN recovery items to be skipped. On item recovery error, the log is shut down before delayed-write submission so partial checkpoint writeback cannot compromise future recovery. Malformed headers, bad lengths, unknown item types, incompatible UUID/format, readonly devices needing recovery, unknown dirty-log features, bad CRCs, and metadata corruption all fail recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_message.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_message.c

## Purpose
Provides XFS-specific kernel logging, assertion reporting, panic-tag alert conversion, hex dumps, buffer I/O alert rate limiting, and one-time experimental feature warnings.

## Main APIs
- `xfs_printk_level` formats XFS messages with mount/superblock identity and optionally emits stack traces for high error verbosity.
- `_xfs_alert_tag` emits alert messages and converts selected panic-mask tags into `BUG`.
- `asswarn` and `assfail` implement warning/fatal assertion reporting.
- `xfs_hex_dump` prints alert-level hex dumps.
- `xfs_buf_alert_ratelimited` emits per-buffer-target rate-limited alerts.
- `xfs_warn_experimental` warns once per mount for shrink, logged xattrs, and zoned realtime features.

## Key Behavior
Messages include `XFS (<s_id>):` when a mounted superblock is available, otherwise `XFS:`. Assertions use `WARN_ON` unless configured to BUG on assertion failure. Experimental warnings are gated by mount opstate bits so each feature warning is emitted once.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_message.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_message.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_message.h

## Purpose
Declares and wraps XFS logging helpers used throughout the filesystem.

## Main Contents
Defines level-specific macros `xfs_emerg`, `xfs_alert`, `xfs_crit`, `xfs_err`, `xfs_warn`, `xfs_notice`, `xfs_info`, and debug-only `xfs_debug`. It also defines rate-limited and once-only wrappers, alert-tag logging, assertion function declarations, hex dump support, buffer alert rate limiting, and the experimental feature enum.

## Integration
The macros emit printk index metadata and dispatch to `xfs_printk_level`, preserving subsystem-indexed format strings while keeping mount-aware formatting in the implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_message.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mount.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mount.c

## Purpose
Implements XFS mount and unmount orchestration, superblock reading, UUID uniqueness tracking, filesystem geometry setup, log recovery sequencing, free-space reservations, summary counter handling, atomic-write limits, and mount-time teardown paths.

## Main APIs
- `xfs_readsb` reads and verifies the primary superblock, first using device sector size and then filesystem sector size.
- `xfs_mountfs` performs full mount setup from superblock normalization through log recovery, quota setup, root/realtime inode loading, reservations, and background worker startup.
- `xfs_unmountfs` flushes inodegc/blockgc/quota/log state, writes a clean unmount, releases in-core structures, and unregisters mount resources.
- `xfs_fs_writable` checks freeze, shutdown, and readonly state.
- `xfs_dec_freecounter` and `xfs_add_freecounter` maintain per-cpu free block/realtime counters plus reserved pools.
- `xfs_add_incompat_log_feature` and `xfs_clear_incompat_log_features` manage primary-superblock log-incompat bits.
- `xfs_set_max_atomic_write_opt` validates and stores the mount atomic-write limit.

## Mount Flow
The mount path computes btree heights and inode geometry, validates/imports stripe alignment, initializes sysfs/debug/error infrastructure, enforces UUID uniqueness, checks data/log device sizes, initializes realtime and per-AG/rtgroup state, starts log mount and first-stage recovery, loads metadata/root/realtime inodes, validates summary counts, initializes quotas, finishes log recovery, and reserves critical metadata/free-space pools.

## Counter and Reservation Behavior
The file sets low-space thresholds, recomputes summary counters after unclean mounts or sick counters, restores realtime free extent counts when needed, reserves default emergency pools, and prevents regular allocations from consuming blocks needed by allocation btrees or privileged metadata transactions.

## Unmount and Error Paths
Unmount forces the log, drains busy extents/discards, stops inodegc/blockgc/zonegc, pushes the AIL, reclaims inodes, unmounts quotas/realtime structures, clears UUID registration, and tears down per-AG/rtgroup/sysfs/error-tag state. Partial mount failures follow ordered cleanup to cancel log recovery, flush reclaim, drain buffer targets, and release initialized subsystems.

## Feature Handling
The file corrects old `features2` alignment issues, promotes v2 inode support, handles logged xattr opstate, validates unknown dirty-log features before recovery, computes group-level atomic write maxima from kernel limits, reflink capacity, and hardware constraints, and supports zoned realtime mount/GC setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mount.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mount.h

## Purpose
Defines the central `struct xfs_mount`, mount feature bits, operational state bits, shutdown flags, counter helpers, group geometry, error configuration, and public mount/counter APIs.

## Main Types
`struct xfs_mount` stores the in-core superblock, VFS superblock, log/AIL pointers, device targets, root and metadata inodes, quota state, directory geometry, workqueues, btree geometry, allocation/realtime group geometry, counters, mount features, opstate bits, health/debug/sysfs state, zoned state, inodegc state, pNFS generation, and UUID table index.

`struct xfs_groups` describes allocation-group and realtime-group geometry, sparse group addressing, device start offset, DAX/device mapping behavior, and maximum atomic write unit. `struct xfs_freecounter` wraps per-cpu free counts plus reserve accounting. `struct xfs_error_cfg` stores retry configuration for error classes.

## Feature and State Helpers
The header defines active filesystem feature bits such as CRCs, reflink, rmapbt, realtime, metadir, and zoned, plus mount-option features such as discard, filestreams, DAX policy, norecovery, and nouuid. Inline helpers test or add features. Opstate helpers atomically test/set/clear clean, shutdown, readonly, inodegc/blockgc, quota resume, logged xattrs, and zonegc state.

## Public API
Declares mount/unmount, superblock read/free, writable checks, device readonly checks, freecounter operations, summary recalc forcing, log incompat feature management, delayed allocation accounting, atomic write option validation, and group-type-to-buftarg mapping.

## Compile-Time Behavior
Quota opstate helpers become no-ops when quota support is disabled. Some v4-era feature checks compile as always true when v4 support is disabled, allowing dead-code elimination.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.c

## Purpose
Implements a generic XFS most-recently-used cache with radix-tree lookup, grouped time-bucket expiry, delayed-work reaping, and client-provided element freeing.

## Main APIs
- `xfs_mru_cache_init` and `xfs_mru_cache_uninit` create/destroy the global MRU reaper workqueue.
- `xfs_mru_cache_create` allocates a cache with lifetime, group count, private data pointer, and free callback.
- `xfs_mru_cache_destroy` flushes and frees a cache.
- `xfs_mru_cache_insert` inserts a caller-provided element under a key.
- `xfs_mru_cache_remove` removes an element without freeing it.
- `xfs_mru_cache_delete` removes and frees an element.
- `xfs_mru_cache_lookup` returns an element and moves it to the current MRU bucket while leaving the cache spinlock held.
- `xfs_mru_cache_done` releases the lookup-held spinlock.

## Key Behavior
Elements live in both a radix tree and a time-bucket list. The bucket array represents coarse time intervals; touching an item moves it to the current MRU bucket. Reaping migrates expired LRU buckets to a reap list and frees them outside the spinlock via the client callback.

## Lifetime and Locking
The implementation adds an extra bucket so elements are not reaped early. Depending on timer granularity, an inactive element can survive up to roughly one group interval beyond the requested lifetime. Internal state is protected by a spinlock. Insert preloads the radix tree before locking and frees the element through the callback on insert failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.h

## Purpose
Declares the XFS MRU cache interface and cache element header.

## Main Contents
Defines `struct xfs_mru_cache_elem` with a list node and unsigned long key, plus `xfs_mru_cache_free_func_t` for client cleanup callbacks. Declares global initialization, cache create/destroy, insert/remove/delete, lookup, and lookup completion APIs.

## Usage Contract
Callers embed or allocate an `xfs_mru_cache_elem` for each cached object. Successful lookups keep the internal spinlock held until `xfs_mru_cache_done` is called.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.c

## Purpose
Implements DAX device failure notification for XFS, translating failed byte ranges into filesystem blocks, reporting affected media, killing DAX users, invalidating page cache, and shutting down the filesystem when metadata or unrecoverable mappings are affected.

## Main API
Exports `xfs_dax_holder_operations` with `.notify_failure = xfs_dax_notify_failure`, used by the DAX holder mechanism.

## Data and Realtime Device Handling
For data and realtime devices, failure ranges are clipped to the filesystem’s device extent, converted to data FSBs or realtime blocks, and mapped to AGs or realtime groups. The code requires rmapbt support to identify file owners. It queries rmap records in each affected group, kills processes for incore DAX file mappings, invalidates cache during pre-remove, and reports data loss through `fserror_report_data_lost`.

## Log Device Handling
External log failures are translated to log daddrs and reported to health monitoring. Normal log corruption notifications shut down the filesystem as on-disk corruption. Pre-remove notifications avoid log-device corruption shutdown and allow forced unmount flow.

## Pre-Remove Behavior
For `MF_MEM_PRE_REMOVE`, the filesystem is frozen to prevent new mappings where possible, all affected mappings are processed, and the filesystem is force-shutdown for unmount. The thaw path also releases userspace freeze state because the device is being removed.

## Failure Handling
Non-inode rmap owners, attr fork mappings, bmbt blocks, inode lookup failures, rmap query errors, or metadata exposure request shutdown with `SHUTDOWN_CORRUPT_ONDISK` outside pre-remove. Out-of-filesystem ranges return `-ENXIO`; missing rmapbt returns `-EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.h

## Purpose
Tiny header exposing XFS DAX failure notification operations.

## API
Declares `extern const struct dax_holder_operations xfs_dax_holder_operations;`.

## Dependencies
The implementation lives in `xfs_notify_failure.c`; including code must have DAX holder type declarations available through normal kernel headers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_platform.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_platform.h

## Purpose
Provides the Linux-kernel platform layer for XFS: common kernel includes, XFS scalar typedefs, configuration-derived debug macros, global parameter aliases, platform utility wrappers, assertions, corruption detection, realtime feature helpers, and memory-to-page conversion.

## Main Contents
Defines XFS core integer types such as `xfs_off_t`, `xfs_ino_t`, `xfs_daddr_t`, `xfs_dev_t`, and `xfs_nlink_t`. It includes major XFS internal headers needed widely by implementation files and maps XFS tunables to `xfs_params`.

## Utility Contracts
Provides wrappers and macros for current-task flag nesting, block-device I/O sizing, errno aliases, return-address capture, sorting, stack traces, 64-bit division helpers, power-of-two helpers, device number translation, and `xfs_rw_bdev`.

## Debug and Corruption Handling
Maps Kconfig options to `DEBUG`, `DEBUG_EXPENSIVE`, `XFS_ASSERT_FATAL`, and `XFS_WARN`. Defines `ASSERT_ALWAYS`, debug/warn/no-op `ASSERT`, and `XFS_IS_CORRUPT`, which reports corruption through `xfs_corruption_error` before returning true.

## Feature Helpers
Defines realtime inode/mount predicates depending on `CONFIG_XFS_RT`, pointer printk formatting for debug builds, and `kmem_to_page` for translating vmalloc or linear kernel memory into pages for I/O routines.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_platform.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.c

## Purpose
Implements XFS support for pNFS block layouts: breaking leased layouts, exporting filesystem UUID/device identity, mapping file ranges to block layouts, and committing client-written blocks back into stable XFS metadata.

## Main APIs
- `xfs_break_leased_layouts` recalls outstanding pNFS layouts before operations that remove blocks or require local writer synchronization.
- `xfs_fs_get_uuid` returns the filesystem UUID and its offset in the on-disk superblock.
- `xfs_fs_map_blocks` maps a file byte range to an iomap for pNFS clients.
- `xfs_fs_commit_blocks` converts written extents, invalidates page cache, updates inode timestamps/size, and commits synchronously.

## Mapping Behavior
`xfs_fs_map_blocks` rejects shutdown filesystems, realtime inodes, and reflink inodes. It takes exclusive IOLOCK, flushes and invalidates page cache, reads the data fork mapping, and returns an iomap plus mount generation. For write layouts over holes, it allocates direct extents, updates timestamps and prealloc state, and forces the inode log so exported blocks survive server crash.

## Commit Behavior
`xfs_fs_commit_blocks` invalidates affected page-cache ranges, converts unwritten extents to written extents, optionally validates that a size extension lands in an allocated written block, then commits inode metadata synchronously. It relies on the caller to provide timestamp updates so a transaction is always committed.

## Correctness Notes
The implementation avoids VFS `file_modified` helpers because pNFS modifies inode metadata directly. It strips SUID/SGID as needed, sets `XFS_DIFLAG_PREALLOC` to protect allocated extents before the client commits, and uses IOLOCK/ILOCK ordering to serialize local and remote layout activity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.h

## Purpose
Declares XFS pNFS block layout integration points.

## Main Contents
When `CONFIG_EXPORTFS_BLOCK_OPS` is enabled, declares UUID export, block mapping, block commit, and layout-break APIs. When disabled, provides a stub `xfs_break_leased_layouts` that succeeds without doing work.

## Integration
The implementation lives in `xfs_pnfs.c` and is used by XFS export/VFS paths that must coordinate file extent changes with outstanding pNFS layouts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.c

## Purpose
Implements a small XFS parallel work abstraction for large, naturally parallel tasks. It wraps a workqueue, shared mount pointer, worker callback, outstanding-work count, first-error capture, and polling support.

## Main APIs
- `xfs_pwork_init` allocates a tagged unbound/freezable/sysfs workqueue and initializes the control object.
- `xfs_pwork_queue` initializes and queues one embedded `struct xfs_pwork`.
- `xfs_pwork_poll` waits for outstanding work to drain while touching the soft-lockup watchdog.
- `xfs_pwork_destroy` destroys the workqueue and returns the first recorded worker error.

## Behavior
Each queued work item calls the caller-provided `work_fn(mp, pwork)`. The first nonzero error is stored in `pctl->error`; work processing is not automatically stopped, so workers are expected to check `xfs_pwork_want_abort` or `xfs_pwork_ctl_want_abort` when appropriate. Completion decrements `nr_work` and wakes poll waiters when the count reaches zero.

## Debug Support
In debug builds, `xfs_globals.pwork_threads` can override the workqueue parallelism. A requested thread count of zero means no explicit concurrency limit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.h

## Purpose
Declares the XFS parallel workqueue abstraction.

## Main Types
`xfs_pwork_work_fn` is the callback signature. `struct xfs_pwork_ctl` stores the workqueue, mount, callback, poll waitqueue, outstanding item count, and first error. `struct xfs_pwork` embeds a `work_struct` plus backpointer to the control object.

## API and Contract
Declares init, queue, destroy, and poll helpers. Provides `XFS_PWORK_SINGLE_THREADED` and inline abort predicates. Callers embed `struct xfs_pwork` in their own work records and should stop early when the control object records an error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.h -->