# subset-b-005799 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log_recover.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_log_recover.c

Purpose: Implements XFS journal discovery and replay during mount, including head/tail detection, CRC validation, stale-log clearing, two-pass item replay, intent replay, unlinked inode cleanup, and final recovery cancellation. It is the core bridge between the on-disk log format and mount-time filesystem consistency.

Important APIs, types, and functions: `xlog_recover`, `xlog_recover_finish`, and `xlog_recover_cancel` are the external recovery lifecycle entry points. `xlog_find_head`, `xlog_find_tail`, `xlog_verify_head`, `xlog_verify_tail`, and `xlog_clear_stale_blocks` locate a safe replay range and protect future mounts from partial records. `xlog_do_recovery_pass`, `xlog_recover_process`, `xlog_recover_process_data`, and `xlog_recover_commit_trans` parse log records and dispatch recovered items through `struct xlog_recover_item_ops`. `xlog_recover_intent_item`, `xlog_recover_process_intents`, `xlog_recover_finish_intent`, and `xlog_recover_release_intent` integrate deferred intent recovery with the AIL and `xfs_defer`. `xlog_recover_iget` and `xlog_recover_iget_handle` safely acquire inodes for logged intent replay, including generation validation in the handle variant.

Control flow: Recovery starts by reading sector-aligned log buffers through `xlog_bread`/`xlog_bwrite`, validating block ranges with `xlog_verify_bno`. Head search handles zeroed logs, cycle transitions, wraparound, partial records, and log v2 multi-block headers. Tail search finds the preceding record, initializes in-core log state, detects clean unmount records, performs CRC-based torn-write trimming, and clears stale blocks beyond the head when writable. Dirty logs run `xlog_do_log_recovery`, which first records cancelled buffer items and then replays active items. After root and realtime metadata are available, `xlog_recover_finish` processes recovered intents, forces the log, rebuilds AGI unlinked lists, and recovers leftover CoW staging extents.

State and persistence behavior: The file mutates `struct xlog` fields such as `l_curr_cycle`, `l_curr_block`, `l_prev_block`, `l_tail_lsn`, `l_recovery_lsn`, `r_dfops`, and opstate bits including `XLOG_ACTIVE_RECOVERY` and `XLOG_RECOVERY_NEEDED`. It writes empty log records to stale regions, replays logged buffer and inode state to metadata, rereads and reinitializes the superblock after replay, and can force shutdown on unrecoverable log or metadata I/O errors. Clean unmount detection sets mount clean state and advances the tail so future log writes point after the unmount record.

Dependencies and integration points: Depends on log format definitions, buffer I/O, AIL, transaction recovery, per-item recovery ops from buffer/inode/dquot/quota/intent modules, quota attachment, reflink recovery, AG iteration, AGI readers, inodegc, and `xfs_error` reporting. It is invoked from the mount path through `xfs_log_mount` and `xfs_log_mount_finish`, and its item dispatch table is extended by log item recovery modules that export `xlog_*_item_ops`.

Risks: Boundary arithmetic around circular log wrap, sector alignment, and variable log v2 headers is high risk. CRC failure handling intentionally treats nearby failures as torn writes, so incorrect distance calculations can drop valid records or replay corrupt ones. Transaction assembly validates flags, lengths, region counts, client ids, and item types; gaps here become metadata corruption. Intent replay must maintain ordering and AIL reference rules or leave pinned intents behind. AGI unlinked-list cleanup deliberately clears unrecoverable buckets, trading leaked unlinked inodes for mount progress.

Test signals: Exercise clean unmount, dirty replay, totally and partially zeroed logs, external and internal logs, read-only devices, log v1/v2 headers, torn writes near head, bad UUID/format, bad CRC on v5 filesystems, unknown log incompat bits, cancelled buffers, intent/done pairs, unfinished intents, unlinked inode buckets, CoW staging recovery, and forced I/O shutdown paths. Fault injection through log recovery delay and metadata/log I/O errors should confirm shutdown and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log_recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_message.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_message.c

Purpose: Provides XFS-specific printk, assertion, panic-tag, hex dump, rate-limited buffer alert, and experimental-feature warning helpers. It centralizes message formatting around an optional `struct xfs_mount` so diagnostics include the mounted device id when available.

Important APIs, types, and functions: `xfs_printk_level` formats variadic messages and may emit a stack trace for severe messages when `xfs_error_level` is high. `_xfs_alert_tag` optionally transforms selected alert tags into `BUG()` via `xfs_panic_mask`. `asswarn` and `assfail` implement assertion reporting for warning and fatal modes. `xfs_hex_dump` wraps `print_hex_dump`. `xfs_buf_alert_ratelimited` uses the buffer target I/O error ratelimit state. `xfs_warn_experimental` maps experimental feature ids to one-time mount opstate warnings.

Control flow: Public wrappers build `struct va_format` and call private `__xfs_printk`, which chooses either `XFS (<s_id>)` or plain `XFS` prefixes. Panic-tag alerts test the global panic mask before printing. Experimental warnings use `xfs_should_warn` to set and test per-mount warning bits.

State and persistence behavior: No persistent disk state is modified. Runtime state includes global error/panic tunables and mount opstate warning bits. Assertion helpers can trigger WARN or BUG depending on build and runtime settings.

Dependencies and integration points: Included widely through `xfs_message.h` and `xfs_platform.h`. Uses Linux printk, ratelimit, BUG/WARN, and XFS mount state. The buffer alert helper integrates with `struct xfs_buftarg` error throttling.

Risks: Misclassified log levels could suppress stack traces or over-trigger them. Panic mask behavior is intentionally dangerous for debugging and should not be enabled casually. Callers must avoid passing invalid mount or buffer pointers on error paths.

Test signals: Build in DEBUG, XFS_WARN, and normal modes; verify mount-tagged and unmounted messages; confirm stack traces for high error level severe messages; validate panic-tag conversion under controlled fault injection; check experimental warnings are emitted once per mount state bit; exercise buffer I/O error storms for ratelimit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_message.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_message.h

Purpose: Declares the XFS diagnostic API and macro layer used throughout the filesystem for severity-specific logging, ratelimited logging, once-only logging, assertions, hex dumps, tagged alerts, buffer alerts, and experimental feature warnings.

Important APIs, types, and functions: Defines `xfs_emerg`, `xfs_alert`, `xfs_crit`, `xfs_err`, `xfs_warn`, `xfs_notice`, `xfs_info`, and conditional `xfs_debug`. `xfs_printk_index_wrap` emits printk index metadata before calling `xfs_printk_level`. `xfs_alert_tag` wraps `_xfs_alert_tag`. Ratelimited and once macros generate per-callsite static state. `enum xfs_experimental_feat` currently covers shrink, logged extended attributes, and zoned realtime devices.

Control flow: Macros forward format strings and arguments to implementation functions while preserving printf checking. DEBUG builds route `xfs_debug` to printk; non-DEBUG builds compile it away. Ratelimited macros call a selected XFS logging macro only when the local ratelimit permits.

State and persistence behavior: Header has no direct storage beyond static ratelimit state emitted at call sites. Experimental warnings rely on mount opstate bits managed by `xfs_message.c`.

Dependencies and integration points: Pulls in `linux/once_lite.h`, forward declares `struct xfs_mount`, and is included by `xfs_platform.h`, making it part of the base include surface for nearly all XFS source files.

Risks: Since most interfaces are macros, side-effecting arguments must be safe under ratelimit/once behavior. The printk-index wrapper must stay consistent with the actual printed format for indexing tools. Adding experimental enum values requires updating the implementation table.

Test signals: Compile with and without DEBUG; run sparse/format checking for printf attributes; confirm ratelimited call sites maintain independent state; add an experimental enum only with matching implementation table coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mount.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_mount.c

Purpose: Implements XFS mount and unmount orchestration, superblock reading, mount-time geometry derivation, UUID uniqueness, log mounting and recovery sequencing, quota/realtime/zoned setup, reserve-pool management, superblock feature updates, writable-state checks, and core free-space counters.

Important APIs, types, and functions: `xfs_readsb`, `xfs_mountfs`, `xfs_unmountfs`, `xfs_freesb`, `xfs_fs_writable`, `xfs_dev_is_read_only`, `xfs_sb_validate_fsb_count`, `xfs_set_low_space_thresholds`, `xfs_default_resblks`, `xfs_mount_reset_sbqflags`, `xfs_add_freecounter`, `xfs_dec_freecounter`, `xfs_force_summary_recalc`, `xfs_add_incompat_log_feature`, `xfs_clear_incompat_log_features`, `xfs_mod_delalloc`, and `xfs_set_max_atomic_write_opt` are the main exported behaviors. Internal helpers cover UUID table management, stripe alignment validation, device-size probes, mount setup for inode geometry and metadir, btree maxlevels, summary-counter repair, and unmount inode flushing.

Control flow: `xfs_readsb` performs a two-stage superblock read, first using device sector size and then the filesystem sector size with verifiers. `xfs_mountfs` applies common superblock geometry, fixes feature2 alignment, validates mount-specified stripe settings, computes btree geometry, initializes sysfs/debug/error tags/UUID, checks devices, initializes realtime, directory, transaction, per-AG and rtgroup structures, starts log recovery, starts background GC, loads metadir/root/realtime inodes, checks counters, initializes quotas, finishes log recovery, cleans read-only mounts when needed, starts zoned handling, reserves free space, and computes atomic write limits. Error labels unwind each stage in reverse. `xfs_unmountfs` flushes inodegc/blockgc, tears down quotas, realtime, root/metadir inodes, log, UUID, stats, sysfs, perag, and rtgroup state.

State and persistence behavior: Mutates `struct xfs_mount`, incore superblock fields, mount feature/opstate bits, UUID xarray entries, percpu counters, reserve pools, delayed allocation counters, log incompat feature bits, and superblock buffer contents. It can synchronously write the superblock for alignment, feature, quota, and log incompat updates. It reconstructs summary counters after unclean mounts and can mark filesystem sickness for later repair.

Dependencies and integration points: Integrates with almost every core XFS subsystem: superblock verifiers, buffer targets, allocation and bmap geometry, inode allocation, realtime allocator, rmap/refcount/reflink, directory/attr geometry, transactions, log manager and recovery, quota manager, inode cache and inodegc, sysfs/debugfs, scrub stats, health and health monitor, zoned allocator, perag/rtgroup management, and VFS freeze/read-only semantics.

Risks: The mount sequence has many dependencies where ordering is critical: geometry before inode lookup, log recovery before trusting counters, root/realtime inodes before intent finishing, and quota resampling after recovery. Error unwinds must not leak perag, rtgroup, log, inode, quota, sysfs, UUID, or worker state. Counter batching and reserve-pool logic must avoid underflow and premature ENOSPC while not overcommitting metadata-reserved blocks. Log incompat feature writes must be serialized and durable before protected log items are emitted.

Test signals: Cover normal mount/unmount, failed reads, bad sector sizes, duplicate/null UUID, stripe option changes, v4/v5 feature combinations, external log and realtime devices, metadir, zoned RT, quota resume, dirty and clean log recovery, read-only recovery, ENOSPC reserve failures, atomic write mount options, forced shutdown, and every mount error label through fault injection. Counter tests should stress concurrent `xfs_dec_freecounter` and reserve depletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mount.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_mount.h

Purpose: Defines the central `struct xfs_mount` and mount-wide feature, opstate, counter, group, error, inodegc, and helper interfaces used by the XFS implementation.

Important APIs, types, and functions: Key types include `struct xfs_error_cfg`, `struct xfs_inodegc`, `struct xfs_groups`, `struct xfs_freecounter`, and `xfs_mount_t`. Feature helpers are generated by `__XFS_HAS_FEAT`, `__XFS_ADD_FEAT`, v4-aware variants, and specialized helpers such as `xfs_has_rtgroups`, `xfs_has_rtrmapbt`, and `xfs_can_sw_atomic_write`. Opstate helpers generated by `__XFS_IS_OPSTATE` cover clean, shutdown, read-only, inodegc, blockgc, quota resume, logged xattrs, and zoned GC. Counter helpers wrap free block/extent accounting and delayed allocation updates. Function declarations expose mount lifecycle, superblock I/O, writable checks, shutdown, log incompat features, and atomic write options.

Control flow: This header does not execute standalone logic except inline helpers. Callers use it to inspect immutable mount features, manipulate opstate bits through atomic bit operations, convert daddrs to allocation-group coordinates, compare and sum percpu counters, and locate the correct buffer target for data or realtime group types.

State and persistence behavior: `struct xfs_mount` separates read-mostly mount geometry and feature fields from frequently modified counters and locks. It carries persistent-superblock mirrors (`m_sb`), runtime-only pointers (log, root inode, buftargs, workqueues), counters, opstate bits, health bits, group xarrays, quota state, and debug/sysfs objects. The header establishes which state is protected by `m_sb_lock`, atomics, percpu counters, RCU, mutexes, or workqueue lifecycle.

Dependencies and integration points: Forward declares core XFS objects and depends on feature constants from superblock format headers, Linux percpu counters, xarrays, workqueues, shrinkers, cpumasks, and XFS group types. It is included by most XFS source files and is therefore an ABI-like internal contract.

Risks: Adding fields to `struct xfs_mount` can affect cacheline layout and lock contention. Feature helpers must reflect superblock semantics exactly, especially v4/v5 compile-time support. Opstate values are bit positions, so renumbering is risky. Counter helpers hide batching semantics; misuse can create stale free-space estimates or reserve accounting bugs.

Test signals: Compile coverage across `CONFIG_XFS_SUPPORT_V4`, quota, realtime, scrub stats, DEBUG, and zoned configurations. Static analysis should verify lock expectations for health fields and counters. Runtime tests should exercise opstate transitions during mount, remount, shutdown, unmount, inodegc/blockgc toggling, and quota resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.c

Purpose: Implements a generic XFS most-recently-used cache with radix-tree lookup and time-bucketed LRU reaping. Clients provide element lifetime, bucket count, callback data, and a free callback.

Important APIs, types, and functions: Public APIs include `xfs_mru_cache_init`, `xfs_mru_cache_uninit`, `xfs_mru_cache_create`, `xfs_mru_cache_destroy`, `xfs_mru_cache_insert`, `xfs_mru_cache_remove`, `xfs_mru_cache_delete`, `xfs_mru_cache_lookup`, and `xfs_mru_cache_done`. Internal `struct xfs_mru_cache` stores the radix tree, list array, reap list, spinlock, bucket timing, delayed work, free callback, and client data. `_xfs_mru_cache_migrate`, `_xfs_mru_cache_list_insert`, `_xfs_mru_cache_clear_reap_list`, and `_xfs_mru_cache_reap` implement expiration and workqueue processing.

Control flow: Module initialization creates a reclaim-safe per-cpu workqueue. Cache creation allocates one extra group to avoid early reaping, initializes lists and radix tree, and arms delayed work on first insert. Insert preloads radix-tree memory, adds the element under lock, and assigns it to the current MRU bucket. Lookup holds the spinlock on successful return, moves the element to the current MRU bucket, and requires the caller to call `xfs_mru_cache_done`. Migration advances `time_zero`, moves expired bucket contents to `reap_list`, and returns the next wakeup time. Reaping removes expired entries from the radix tree under lock and invokes client free callbacks without the lock.

State and persistence behavior: Cache state is memory-only. Time is represented in jiffies; expiration granularity is `lifetime / group_count` plus one extra bucket. Work scheduling state is kept in `queued`. No disk state is changed, but callers may use free callbacks for filesystem-specific teardown.

Dependencies and integration points: Uses Linux radix trees, delayed work, workqueues, spinlocks, and lists. The header exposes an opaque cache type and element node contract so XFS features such as filestreams can cache keyed objects without embedding cache internals.

Risks: Successful lookup returns with the cache spinlock held, which is easy to misuse. Free callbacks run unlocked and must tolerate concurrent cache state changes. Jiffies wrap and delayed reaper lag are handled by migration logic but remain sensitive to bucket arithmetic. Duplicate keys fail insertion and the passed element is freed through the callback.

Test signals: Validate create parameter rejection, insert/lookup/touch movement, duplicate insert cleanup, remove without callback, delete with callback, expiration timing across buckets, destroy while work is queued, and callback execution outside the spinlock. Stress with many keys and delayed reaper execution to ensure no leaked list entries or radix-tree entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.h

Purpose: Declares the opaque MRU cache interface and the element structure that clients must allocate and pass to the cache.

Important APIs, types, and functions: `struct xfs_mru_cache_elem` contains the intrusive list node and unsigned long key. `xfs_mru_cache_free_func_t` defines the callback used for deletion and error cleanup. Public functions cover global workqueue init/uninit, cache create/destroy, insert, remove, delete, lookup, and lookup completion.

Control flow: Clients create a cache with lifetime and group count, allocate elements embedding or containing `struct xfs_mru_cache_elem`, insert by key, use lookup plus `xfs_mru_cache_done` for locked access, and destroy the cache to flush all elements.

State and persistence behavior: The header exposes no persistent state. The element key is stored in each element so the implementation can remove radix-tree entries while walking expiration lists.

Dependencies and integration points: Depends on Linux list infrastructure through the element. The cache is intentionally generic and opaque so users do not depend on radix-tree or timing internals.

Risks: The locked-return lookup API must be documented at every call site; failing to call `xfs_mru_cache_done` deadlocks the cache. Passing stack or shared elements can corrupt lists because the cache owns the list node until removal/free.

Test signals: Compile users with sparse lock annotations; verify all successful lookup paths call `xfs_mru_cache_done`; validate callback ownership conventions in each cache user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_notify_failure.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_notify_failure.c

Purpose: Implements DAX holder failure notification for XFS. It translates physical DAX failure ranges into filesystem/log/realtime ranges, reports media errors, kills affected DAX mappings, invalidates pages for pre-remove, and shuts down or force-unmounts when metadata or log integrity is at risk.

Important APIs, types, and functions: Exports `xfs_dax_holder_operations` with `.notify_failure = xfs_dax_notify_failure`. Internal `struct xfs_failure_info` tracks group-relative failure ranges, memory-failure flags, and whether a shutdown is required. `xfs_dax_translate_range` maps DAX device offsets to XFS daddrs and basic-block lengths. `xfs_dax_notify_logdev_failure` handles external-log failures. `xfs_dax_notify_dev_failure` walks data or realtime reverse maps. `xfs_dax_failure_fn` processes each rmap owner and calls `mf_dax_kill_procs`, page invalidation, and `fserror_report_data_lost`.

Control flow: The DAX core calls `xfs_dax_notify_failure`; XFS rejects notifications before the superblock is born, dispatches external log devices separately, otherwise treats the DAX device as data or realtime. Device failures are range-clipped to the filesystem area, reported to health monitoring, and require rmapbt support to identify affected owners. Pre-remove freezes the filesystem to stop new mappings, iterates groups and rmap records under an empty transaction, then force-shuts down for unmount and thaws. Non-pre-remove failures shut down if metadata/non-inode owners are encountered or if rmap/query/DAX kill operations fail.

State and persistence behavior: Does not repair disk state. It can freeze/thaw the superblock, invalidate page cache ranges, report lost data to fs error reporting, notify healthmon, and force shutdown with `SHUTDOWN_FORCE_UMOUNT` or `SHUTDOWN_CORRUPT_ONDISK`. It reads AGF or realtime rmapbt state under transaction context.

Dependencies and integration points: Integrates with Linux DAX holder operations, memory failure flags, filesystem freeze/thaw, reverse mapping btrees, realtime groups, XFS health monitor, inode cache, page cache invalidation, and VFS address spaces. `xfs_buf.c` attaches these operations to DAX buffer targets.

Risks: Correct range clipping is essential for partition offsets and whole-device notifications. Without rmapbt the function cannot identify affected files and returns unsupported. Pre-remove must thaw even after errors. Metadata owners cannot be remediated at file granularity and force shutdown. Group/rmap cursor teardown must release AG/RT locks and references on every path.

Test signals: Inject DAX failures for data, external log, realtime, whole-device, out-of-range, pre-remove, file data, attr fork, bmbt block, metadata owner, non-incore inode, and rmap query errors. Verify healthmon reports device type and range, DAX processes are killed for mapped files, page cache invalidates on pre-remove, freeze/thaw balance is maintained, and shutdown flags match failure mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_notify_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_notify_failure.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_notify_failure.h

Purpose: Declares the XFS DAX holder operations object used to receive media failure notifications from DAX devices.

Important APIs, types, and functions: Exposes `extern const struct dax_holder_operations xfs_dax_holder_operations`.

Control flow: Consumers include this header and register the operations with DAX-capable buffer targets. The actual callback implementation lives in `xfs_notify_failure.c`.

State and persistence behavior: No state is stored in the header. Runtime effects are entirely in the registered operations.

Dependencies and integration points: Relies on Linux `struct dax_holder_operations` being visible to includers. It is integrated by the buffer target setup path for DAX devices.

Risks: If the operations object is not registered for a DAX target, media failure callbacks will not reach XFS. Header changes should remain minimal to avoid leaking implementation details.

Test signals: Build DAX-enabled configurations and confirm `xfs_buf.c` references the exported object; trigger a synthetic DAX notify path and observe dispatch into XFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_notify_failure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_platform.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_platform.h

Purpose: Provides the Linux kernel platform adaptation layer for XFS. It gathers common kernel includes, maps configuration options to XFS debug macros, defines XFS core typedefs, pulls in base XFS headers, exposes tunable aliases, and supplies portability helpers and assertions.

Important APIs, types, and functions: Defines `xfs_off_t`, `xfs_ino_t`, `xfs_daddr_t`, `xfs_dev_t`, `xfs_nlink_t`, `struct xfs_kobj`, and `struct xstats`. Provides tunable aliases such as `xfs_panic_mask`, `xfs_error_level`, and timer defaults. Utility helpers include device id conversion, `rounddown_64`, `roundup_64`, `howmany_64`, `isaligned_64`, `log2_if_power2`, `mask64_if_power2`, `delay`, `kmem_to_page`, and `xfs_rw_bdev` declaration. Assertion/corruption macros include `ASSERT_ALWAYS`, build-dependent `ASSERT`, and `XFS_IS_CORRUPT`.

Control flow: The header is included before most XFS implementation files, establishing kernel APIs, endian detection, DEBUG/XFS_WARN behavior, realtime feature stubs, pointer formatting, and the `STATIC static noinline` convention used for testable internal functions.

State and persistence behavior: No direct persistent state. It references global tunables and statistics objects. Assertion and corruption macros can emit warnings, stack traces, or fatal bugs depending on config and runtime settings.

Dependencies and integration points: Integrates XFS with Linux VFS, block layer, memory management, workqueues, sysfs/debugfs, ratelimits, uaccess, endian/unaligned helpers, and XFS base modules such as stats, sysctl, buffer, message, drain, and hooks. It also gates realtime inode checks on `CONFIG_XFS_RT`.

Risks: Because this is a foundational include, changes can affect the entire XFS build. Assertion semantics differ by DEBUG and XFS_WARN, so code must not depend on assertion side effects. `XFS_IS_CORRUPT` reports and evaluates expressions; callers must keep expressions side-effect free. Type widths are part of on-disk format assumptions.

Test signals: Build matrix across DEBUG, DEBUG_EXPENSIVE, ASSERT_FATAL, XFS_WARN, realtime enabled/disabled, big-endian, and v4 support. Static analysis should flag side effects inside assertion and corruption expressions. Runtime fault tests should verify corruption reports include useful caller addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.c

Purpose: Implements XFS support for NFS pNFS block layouts, including layout recall synchronization, filesystem UUID export, block mapping for clients, preallocation and durability for write layouts, and commit handling after clients write directly to storage.

Important APIs, types, and functions: `xfs_break_leased_layouts` recalls outstanding layouts before local operations remove blocks or need synchronization. `xfs_fs_get_uuid` returns the filesystem UUID and its on-disk superblock offset. `xfs_fs_map_blocks` maps file byte ranges to `struct iomap` for pNFS clients, allocating blocks for write layouts when needed. `xfs_fs_commit_blocks` converts unwritten extents, invalidates page cache, updates timestamps/size, and commits synchronously. Internal helpers `xfs_fs_map_update_inode` and `xfs_pnfs_validate_isize` handle inode metadata updates and size validation.

Control flow: Mapping rejects shutdown, realtime inodes, and reflink inodes. It takes `XFS_IOLOCK_EXCL`, bounds the request, flushes and invalidates page cache, reads the data fork map, and for write holes allocates direct I/O blocks, marks the inode preallocated, commits metadata, and forces the inode log before returning an iomap with the mount generation. Commit takes the IOLOCK, invalidates affected pagecache ranges, converts unwritten extents, validates any size extension points into allocated written space, then logs inode timestamps and size in a synchronous transaction.

State and persistence behavior: Can allocate blocks, set `XFS_DIFLAG_PREALLOC`, strip SUID/SGID, update ctime/mtime/atime, update `i_size` and `i_disk_size`, convert unwritten extents, and force log durability so handed-out pNFS layouts survive server crashes. It returns `m_generation` so clients can detect layout changes after growfs.

Dependencies and integration points: Integrates XFS bmap/iomap, transactions, inode locks, pagecache writeback/invalidation, VFS lease layout breaking, exportfs block operations, log force, and mount generation. It is conditionally exposed by `xfs_pnfs.h` under `CONFIG_EXPORTFS_BLOCK_OPS`.

Risks: Layout handing out block addresses is sensitive to stale page cache, delayed allocations, unwritten extents, reflink sharing, realtime-device identity, and crash durability. The code intentionally avoids pNFS for reflink and realtime files. Size extension must not expose holes or unwritten extents as valid EOF. Lock dropping in layout breaking changes IOLOCK mode and must be reflected to callers.

Test signals: Exercise read and write pNFS layouts, holes requiring allocation, EOF extension, unwritten extent conversion, SUID/SGID stripping, pagecache invalidation failures, shutdown, reflink and realtime rejection, layout recall returning `-EWOULDBLOCK`, and growfs generation changes. Crash tests should verify allocated write-layout blocks remain mapped after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.h

Purpose: Declares XFS pNFS block layout hooks when exportfs block operations are enabled and provides a no-op layout break helper otherwise.

Important APIs, types, and functions: Under `CONFIG_EXPORTFS_BLOCK_OPS`, declares `xfs_fs_get_uuid`, `xfs_fs_map_blocks`, `xfs_fs_commit_blocks`, and `xfs_break_leased_layouts`. Without that config, `xfs_break_leased_layouts` is an inline no-op returning success.

Control flow: Build-time configuration selects whether XFS exposes pNFS block layout operations or compiles callers against a stub for layout recall.

State and persistence behavior: The header itself has no state. Enabled implementations may allocate blocks, update inode metadata, and force log durability.

Dependencies and integration points: Ties XFS inode operations to NFS/exportfs block layout support and `struct iomap`. The no-op stub lets non-pNFS builds avoid conditional logic at call sites that merely need to break layouts.

Risks: Callers relying on actual layout recall must only do so in configurations where exportfs block ops are enabled. Prototype changes must stay in sync with NFS/exportfs expected hooks.

Test signals: Build with `CONFIG_EXPORTFS_BLOCK_OPS=y` and disabled; verify callers compile in both modes and pNFS export tests only expect block layout behavior in the enabled mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.c

Purpose: Provides a small parallel workqueue abstraction for XFS tasks that can be split across CPUs while collecting the first error and offering polling that keeps the soft lockup watchdog alive.

Important APIs, types, and functions: `xfs_pwork_init` allocates an unbound, sysfs-visible, freezable workqueue and initializes `struct xfs_pwork_ctl`. `xfs_pwork_queue` initializes and queues an embedded `struct xfs_pwork`. `xfs_pwork_poll` waits for completion with periodic watchdog touches. `xfs_pwork_destroy` destroys the workqueue and returns the recorded error. Internal `xfs_pwork_work` invokes the caller work function, records the first error, decrements the work count, and wakes waiters.

Control flow: Callers initialize a control object with mount, callback, and tag; queue work items embedded in caller-owned structures; optionally poll until `nr_work` reaches zero; then destroy the workqueue to flush and retrieve the first error. DEBUG builds can override the worker count via `xfs_globals.pwork_threads`; otherwise allocation uses no explicit concurrency limit.

State and persistence behavior: State is memory-only in `xfs_pwork_ctl`: workqueue pointer, mount pointer, callback, waitqueue, atomic pending-work count, and first error. No disk state is changed by this layer, though callbacks may perform filesystem work.

Dependencies and integration points: Uses Linux workqueues, waitqueues, atomics, NMI softlockup watchdog touch, XFS tracing, and global sysctl/debug settings. `xfs_iwalk` is a visible user for parallel AG inode walking.

Risks: The first error does not stop already queued work; callbacks must call `xfs_pwork_want_abort` or `xfs_pwork_ctl_want_abort` to cooperate. `xfs_pwork_destroy` relies on workqueue destruction to flush outstanding work, so callers must not free embedded work items early. Polling is intended for lock-heavy mount-like callers and should not replace normal flush semantics blindly.

Test signals: Queue multiple successful and failing work items; confirm first-error retention, wait wakeups, destroy flush, DEBUG thread override, and cooperative abort checks. Exercise mount-time users under soft-lockup-sensitive conditions to verify `xfs_pwork_poll` touches the watchdog while waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.h

Purpose: Declares the XFS parallel work abstraction, including caller-visible control and embedded work structures plus helper functions for queuing, waiting, teardown, and cooperative abort checks.

Important APIs, types, and functions: `xfs_pwork_work_fn` is the callback signature. `struct xfs_pwork_ctl` stores the workqueue, mount, callback, waitqueue, pending count, and first error. `struct xfs_pwork` embeds Linux `work_struct` and a backpointer to the control object. `XFS_PWORK_SINGLE_THREADED` supports callers that need a sentinel pwork object without a control. Inline `xfs_pwork_ctl_want_abort` and `xfs_pwork_want_abort` report whether an error has been recorded.

Control flow: Callers embed `struct xfs_pwork`, initialize a control object, queue embedded work, check abort helpers from callbacks, poll or destroy when done, and consume the returned error.

State and persistence behavior: Header state is transient and memory-only. Error propagation is cooperative and non-atomic beyond simple integer storage; it assumes the workqueue use pattern tolerates first-writer wins without strict ordering.

Dependencies and integration points: Depends on Linux workqueues, waitqueues, and atomics. Used by XFS parallel scans and mount-time work that wants a common kernel-side analogue to xfsprogs workqueues.

Risks: Work item lifetime is caller-owned; freeing containers before workqueue drain is unsafe. The single-threaded sentinel has `.pctl = NULL`, so helpers must tolerate NULL only where intended. Callback implementations must poll abort helpers or work continues after failures.

Test signals: Compile all users with sparse and lockdep; exercise queued and sentinel paths; verify callbacks that detect abort exit promptly and that callers always destroy initialized controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.h -->
