# Research: subset-b-005792

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary_repair.c

Purpose: implements online repair for the XFS realtime summary metadata file. The repair path rebuilds a complete summary into a hidden temporary regular file, writes verifier-ready realtime summary buffers, atomically exchanges the rebuilt data fork with the live rtsummary file, updates in-core realtime summary sizing/cache state, and reaps the old blocks.

Important APIs and functions: `xrep_setup_rtsummary()` creates the staging tempfile and extends the realtime-summary scrub context reservation by `m_rsumblocks` plus worst-case bmap btree overhead. `xrep_rtsummary_prep_buf()` is the `xrep_tempfile_copyin_fn` callback that copies generated summary words from the scrub xfile via `xfsum_copyout`, stamps rtgroup-aware buffer headers when needed, assigns buffer ops, and marks the buffer type. `xrep_rtsummary()` is the repair entry point; it checks feature prerequisites, fixes metadata inode forks, preallocates/copies the replacement file, calls `xrep_tempexch_trans_reserve()` and `xrep_tempexch_contents()`, then reaps the temporary inode fork.

Control flow: setup must happen before scrub while no replacement file size is known, so it reserves a conservative amount of space. Repair rejects filesystems without rmapbt or exchange-range support, exits without action if the scrub-generated rtbitmap block count disagrees with the superblock, repairs fork-level damage, spins on a nonblocking tempfile ILOCK to avoid lock inversion with the rtsummary ILOCK, joins both inodes, preallocates all summary blocks, copies generated block contents to disk buffers, sets the temp file size, reserves exchmaps resources, exchanges mappings, resets cache/geometry, and frees the old data fork from the tempfile.

State and persistence: persistent state changes occur through logged XFS transactions, dirty metadata buffers, atomic mapping exchange, and `xrep_reap_ifork`. The temporary inode is unlinkable and only becomes durable repair state through the exchange. In-core `rtg_rsum_cache`, `m_rsumlevels`, and `m_rsumblocks` are updated after the swap so later realtime allocation code sees the rebuilt summary. Dependencies include `xchk_rtsummary` generated data, realtime bitmap/summary helpers, temp-file/exchmaps repair helpers, metadata inode repair, buffer verifiers, and rmap-based reaping.

Risks and test signals: the repair is sensitive to reservation underestimation because the transaction cannot be dropped while the rtsummary ILOCK is held; feature gating for rmapbt and exchange-range must stay aligned with repair assumptions. Header stamping differs for rtgroups vs legacy realtime filesystems, so tests should cover both formats, corrupted summary blocks, changed rtsummary levels/blocks, copyin failures, termination while polling the tempfile lock, and post-repair scrub of allocation behavior. Existing signals are tracepoints for tempfile copyin/prealloc and rtsummary scrub records plus the generic scrub repair/rescan path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/scrub.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/scrub.c

Purpose: this is the top-level online scrub and repair dispatcher for XFS. It validates ioctl input, maps scrub types to setup/check/repair operations, manages per-operation state and teardown, handles repair retries, updates health and stats, and implements both single-item and vectored scrub ioctls.

Important APIs and functions: `meta_scrub_ops[]` is the central dispatch table keyed by `XFS_SCRUB_TYPE_*`, tying each metadata type to an `xchk_meta_ops` setup, scrub, optional repair, repair revalidation, feature predicate, and input class. `xchk_validate_inputs()` enforces scrub flags, reserved fields, scrub type existence, feature support, per-type selector fields, repair prerequisites, and force-rebuild semantics. `xfs_scrub_metadata()` allocates and drives `struct xfs_scrub`; it runs setup, scrub or repair-eval, health updates, repair attempts, retry handling, stats merge, teardown, and trace emission. `xfs_ioc_scrub_metadata()` and `xfs_ioc_scrubv_metadata()` are the userspace ioctl entry points. `xchk_scrub_create_subord()` and `xchk_scrub_free_subord()` create nested scrub contexts for subordinate checks.

Control flow: the single-item path checks capabilities, copies `xfs_scrub_metadata` from userspace, rejects shutdown/norecovery mounts, validates operation shape, initializes `sc`, optionally takes freeze/write protection for repair, calls the type-specific setup, executes the scrubber, records runtime, updates health, and calls repair if userspace requested it and the flags indicate repairable damage. Repair can return `-EAGAIN` to tear down and retry from setup, allowing a repair/rescrub loop. `-EDEADLOCK` triggers a `TRY_HARDER` retry and `-ECHRNG` enables defer-op draining. The vectored path validates a bounded vector copied from userspace, optionally pins an inode by handle for the whole batch, handles barrier pseudo-items by checking prior results/flags, runs each scrub through `xfs_scrub_metadata()`, optionally sleeps between items, and copies results back.

State and persistence: `xfs_scrub` owns transaction pointers, target inode, optional temporary/orphanage inodes, xfiles, xmbuf targets, AG/rtgroup cursors, locks, sick/healthy masks, and feature-gate flags. `xchk_teardown()` is the key cleanup path: it frees AG and rtgroup resources, commits a repair transaction only when appropriate, cancels clean scrub transactions, releases inode locks/references, drops freeze protection, destroys xfiles/xmbufs, cleans scratch buffers, releases temp/orphanage files, and disables dynamic fs hooks. Persistent changes are delegated to repair functions and committed through transactions; this file controls when the final transaction is committed or canceled.

Dependencies and integration points: this file is the integration boundary between the ioctl ABI (`xfs_scrub_metadata`, `xfs_scrub_vec_head`, `xfs_scrub_vec`), all scrub/repair modules, health reporting, stats, dynamic live-update hooks, tempfile/orphanage helpers, quota/parent/rmap/exchrange subsystems, and mount write-freeze protection. Its dispatch table must stay synchronized with `XFS_SCRUB_TYPE_NR`, scrub type trace names, stats names, feature predicates, and userspace expectations from `xfs_scrub`.

Risks and test signals: risks cluster around dispatch-table drift, accepting invalid selector fields, forgetting teardown for a resource added to `struct xfs_scrub`, incorrect retry flag handling, repair without write/freeze protection, and vector barriers failing open. `copy_from_user`/`copy_to_user` failures and fatal signals need coverage because partial vectors are possible. Test signals include ioctl ABI tests for every scrub type, vectored barrier behavior, repair-required vs no-repair-needed flags, TRY_HARDER/defer-drain retries, shutdown/norecovery/read-only rejection, scrub-by-handle generation mismatch, and trace/stats results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/scrub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/scrub.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/scrub.h

Purpose: defines the shared online scrub/repair state model, operation table contract, scheduler-relax helpers, allocation/iget policy, AG/realtime context structs, top-level `struct xfs_scrub`, subordinate scrub wrappers, state flags, and public scrubber/xref prototypes.

Important APIs and types: `struct xchk_relax` and `xchk_maybe_relax()` rate-limit `cond_resched()` and fatal-signal checks so long scrub loops remain preemptible without paying the cost on every iteration. `XCHK_GFP_FLAGS` standardizes scrub memory allocation as retryable, non-warning, NOFS-compatible kernel allocation. `XCHK_IGET_FLAGS` marks scrub-by-handle inode lookups as untrusted and non-cache-polluting. `enum xchk_type` classifies selector requirements. `struct xchk_meta_ops` is the dispatch-table shape consumed by `scrub.c`. `struct xchk_ag`, `struct xchk_rt`, and `struct xfs_scrub` hold the per-operation working set. `xchk_should_terminate()` wraps relaxation and fatal signal propagation.

Control flow: scrub modules receive an initialized `struct xfs_scrub`, use the embedded AG/rtgroup contexts and lock flags to acquire resources, use `sc->buf`, `sc->xfile`, and `sc->xmbtp` for scratch state, and report findings by setting scrub output flags through common helpers. Long loops call `xchk_should_terminate()` or `xchk_maybe_relax()` to decide whether to bail out with `-EINTR`. Subordinate scrub helpers clone the parent context for nested checks while preserving shared inode/temp/orphanage state and restoring the original scrub type and flags when freed.

State and persistence: this header does not persist data directly, but it defines ownership and lifetime rules for every resource the dispatcher tears down. The `flags` field separates normal scrub state from repair state, including feature gates (`XCHK_FSGATES_*`), retry hints (`XCHK_TRY_HARDER`, `XCHK_NEED_DRAIN`), and repair rescan state (`XREP_ALREADY_FIXED`). `sick_mask` and `healthy_mask` bridge scrub findings to in-core health updates. The fallback macros for realtime and quota scrubbers collapse unsupported builds to `xchk_nothing()`.

Dependencies and integration points: all scrub and repair compilation units include this header. It depends on XFS mount, transaction, inode, btree, buffer, realtime group, and userspace scrub ABI types provided by the surrounding XFS headers. Prototypes connect the central dispatcher to per-metadata scrubbers and cross-reference helpers across allocation, inode, bmap, directory, xattr, symlink, parent, realtime, quota, counters, nlinks, dirtree, and metapath modules.

Risks and test signals: changes to `struct xfs_scrub` are high risk because teardown, subordinate copying, tracepoints, and many scrubbers rely on exact ownership semantics. Incorrect relaxation behavior can create soft-lockup or interruptibility regressions. Prototype or config fallback drift can cause build-only failures under `CONFIG_XFS_RT`, `CONFIG_XFS_QUOTA`, or repair-disabled configurations. Test signals are broad compile-matrix coverage plus long-running scrub cancellation tests and resource leak checks after subordinate scrub failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/scrub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.c

Purpose: implements optional online scrub statistics collection for global and per-mount debugfs reporting. It counts scrub outcomes, repair attempts/successes, retry counts, and accumulated check/repair runtimes per scrub type.

Important APIs and functions: `struct xchk_scrub_stats` stores counters and timing for one scrub type, guarded by a per-type spinlock. `struct xchk_stats` owns the debugfs dentry and an array indexed by `XFS_SCRUB_TYPE_NR`. `name_map[]` maps scrub type numbers to stable debugfs output names. `xchk_stats_format()` emits one line per named scrub type. `xchk_stats_estimate_bufsize()` computes the worst-case output allocation. `xchk_stats_merge_one()` updates a counter bucket from `xfs_scrub_metadata` flags and `xchk_stats_run`. Public entry points allocate/register/free mount stats and set up/tear down global stats.

Control flow: `xfs_scrub_metadata()` accumulates runtime and retry data in `xchk_stats_run` and calls `xchk_stats_merge()` unless the operation ended as `-ENOENT`. Merge updates both `global_stats` and `mp->m_scrub_stats`. Debugfs reads allocate a snapshot buffer, format all stat lines in one pass, and serve it with `simple_read_from_buffer`; reads after position zero return EOF to avoid multi-call garbling. Writing `1` to `clear_stats` resets all counters up to the spinlock field.

State and persistence: stats are in-memory only and disappear on module/mount teardown. Global stats live in static storage; mount stats are allocated under `mp->m_scrub_stats`. Counters are protected by `css_lock`, but formatting reads fields without taking those locks, so debugfs output is a best-effort live snapshot rather than a coherent transaction. The debugfs dentries are attached under a `scrub` directory with `stats` and `clear_stats` files.

Dependencies and integration points: depends on `CONFIG_XFS_ONLINE_SCRUB_STATS`, debugfs helpers, XFS scrub type constants, scrub flags, `ktime_get_ns` timing from `stats.h`, and the mount lifecycle that calls mount stats allocation/free and register/unregister. It must stay aligned with `meta_scrub_ops[]`, trace scrub type names, and the userspace/debugfs tools that parse the fixed text format.

Risks and test signals: risks include missing `name_map` entries when new scrub types are added, integer overflow of long-running 32-bit counters, stale debugfs dentries if unregister/free ordering changes, and snapshot inconsistency during live updates. Buffer-size estimation relies on struct field layout, so adding fields before `css_lock` requires care. Test signals should include stats-disabled builds, mount/global debugfs file presence, clear_stats validation, output line count/name stability, and nonzero counters after clean, corrupt, retry, and repair paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.h

Purpose: declares the optional scrub statistics interface used by the dispatcher and mount lifecycle code. When stats are disabled, it compiles the interface away to no-op macros while preserving call sites.

Important APIs and types: `struct xchk_stats_run` is the per-operation accumulator with `scrub_ns`, `repair_ns`, retry count, and repair attempted/succeeded booleans. Under `CONFIG_XFS_ONLINE_SCRUB_STATS`, the header declares global setup/teardown, mount allocation/free, debugfs register/unregister, and `xchk_stats_merge()`. `xchk_stats_now()` and `xchk_stats_elapsed_ns()` use nanosecond time and force at least one nanosecond elapsed if the clock returns the same value.

Control flow: scrub code initializes an `xchk_stats_run`, samples `xchk_stats_now()` around scrub/repair bodies, adds elapsed time, and merges at the end. The disabled configuration makes all helpers constant or no-op so callers need no `#ifdef` guards. The elapsed helper hides clock-resolution behavior from the dispatcher.

State and persistence: the header owns no state directly; the implementation stores in-memory global and per-mount counters. In disabled builds, no state is allocated and elapsed times are always zero. Dependencies include the XFS mount and scrub metadata types in callers, debugfs `dentry`, and kernel timekeeping.

Risks and test signals: the main risk is semantic drift between enabled and disabled builds, especially if callers start relying on side effects from merge or nonzero time values. The one-nanosecond minimum is important for avoiding misleading zero-duration reports. Test signals should include compile tests with stats enabled and disabled, runtime validation that counters increment only in enabled builds, and repair timing coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink.c

Purpose: implements online scrub setup and validation for XFS symbolic links. It verifies target type, health-zapped state, plausible size, inline target layout, remote target readability, and null-termination consistency.

Important APIs and functions: `xchk_setup_symlink()` allocates a `XFS_SYMLINK_MAXLEN + 1` scratch buffer before taking the inode lock, asks repair setup to create/reserve a temporary symlink when repair is possible, and delegates inode-content setup to `xchk_setup_inode_contents()`. `xchk_symlink()` is the scrubber; it checks `S_ISLNK`, `XFS_SICK_INO_SYMLINK_ZAPPED`, data fork format, `i_disk_size`, inline fork size and `strnlen`, and remote target contents via `xfs_symlink_remote_read()`.

Control flow: setup prepares shared scratch and repair resources, then locks/loads the target inode contents. Scrub rejects non-symlink inodes with `-ENOENT`, treats a zapped symlink sickness as data-fork corruption, validates size bounds, fast-checks inline symlinks against fork capacity and embedded string length, or reads remote target blocks into the scratch buffer and checks that a null byte is not found before the declared length. A clean remote read clears the zapped-health reminder with `xchk_mark_healthy_if_clean()`.

State and persistence: this file is read-only except for health reporting. It stores transient target bytes in `sc->buf` and updates scrub output flags and healthy masks through common helpers. Persistent repair is delegated to `symlink_repair.c`; setup reserves repair blocks only when the request could repair.

Dependencies and integration points: depends on inode-content setup, common scrub health helpers, XFS symlink remote verifiers/read helpers, data fork layout helpers, and the repair setup path. It is wired into `meta_scrub_ops[]` as `XFS_SCRUB_TYPE_SYMLINK` with `xchk_setup_symlink`, `xchk_symlink`, and `xrep_symlink`.

Risks and test signals: risks include off-by-one size/string checks, treating zero-length or overlong targets inconsistently with VFS/XFS symlink creation rules, and remote read errors being converted incorrectly by `xchk_fblock_process_error`. Tests should cover inline and remote symlinks, missing/incorrect data fork format, zapped health state, exact `XFS_SYMLINK_MAXLEN`, truncated remote block contents, and repair setup reservation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink_repair.c

Purpose: repairs corrupted XFS symbolic links by salvaging a plausible target when possible, writing the repaired target into a private temporary symlink, atomically exchanging the temp data fork with the damaged symlink, and reaping/resetting the old target storage.

Important APIs and functions: `xrep_setup_symlink()` creates an unlinkable temporary symlink and reserves space for a worst-case replacement plus mapping exchange overhead. `xrep_symlink_salvage_inline()` and `xrep_symlink_salvage_remote()` recover target bytes from inline fork data or verified-ish remote blocks. `xrep_symlink_salvage()` validates recovered length against `i_disk_size` and falls back to a long explanatory dummy target if nothing reliable can be recovered. `xrep_symlink_rebuild()` writes the chosen target to the temp symlink, commits, allocates exchmaps transaction state, swaps content, and resets the temp fork. `xrep_symlink()` gates repair on rmapbt and exchange-range support and commits the final repair transaction.

Control flow: repair starts under the target inode ILOCK. Salvage skips old content if scrub already observed corruption; otherwise it copies inline bytes or walks remote extents, reading buffers manually and accepting blocks only when header ownership/offset/length are sane and either the verifier passes or the magic value is intact. The buffer is null-terminated and accepted only if `strlen` equals the on-disk size. Rebuild drops the target ILOCK while taking the temp ILOCK to avoid a long lock hold, reserves quota beyond limits for metadata consistency, destroys the temp dummy fork, writes the rebuilt target, commits, reacquires both inodes for exchange, uses local-copy optimization when both forks are inline and fit, otherwise promotes local forks to extent format and exchanges mappings, then frees old remote blocks and resets the temp symlink to a harmless target.

State and persistence: persistent repair uses logged symlink writes, inode core/fork logging, deferred bmap/exchmaps work, quota reservations, and `xrep_reap_ifork`. The temporary symlink is hidden and initialized to a valid dummy target so verifiers remain happy before repair content is written. If all target bytes are lost, repair intentionally persists a long target that cannot resolve as a normal pathname, preventing accidental redirection to an existing file. Health state for `XFS_SICK_INO_SYMLINK_ZAPPED` is cleared when dummy replacement is used.

Dependencies and integration points: integrates with tempfile/exchmaps helpers, XFS symlink write/read/verifier code, bmap conversion, quota reservation, rmap-based reaping, health helpers, tracepoints, and the scrub dispatch entry for `XFS_SCRUB_TYPE_SYMLINK`. It assumes exchange-range support for atomic commit and rmapbt support for safe old-fork cleanup.

Risks and test signals: risks include accepting malicious stale remote blocks during salvage, incorrect owner stamping when local temp symlinks are promoted to remote blocks, exposing old corrupted content to concurrent `readlink()` during rebuild, quota reservation/assertion mismatches, and local/remote conversion bugs around fork sizes. Tests should exercise inline-to-inline copyout, inline-to-remote promotion, remote-to-inline replacement, total target loss/dummy target, zapped inode sickness, remote verifier failure with good/bad magic, fatal termination before exchange, and post-repair rescrub/readlink behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempexch.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/tempexch.h

Purpose: declares the small repair-only interface for atomically exchanging a rebuilt temporary file's fork mappings with the metadata file being repaired.

Important APIs and types: `struct xrep_tempexch` wraps `struct xfs_exchmaps_req`, the exchange request consumed by XFS exchmaps code. `xrep_tempexch_trans_reserve()` prepares/reserves an existing transaction when ILOCKs cannot be dropped. `xrep_tempexch_trans_alloc()` creates a fresh transaction and locks/joins both files for a whole-fork exchange. `xrep_tempexch_contents()` performs the mapping exchange and finishes deferred work.

Control flow: repair modules include this header when they stage rebuilt file-based metadata in a temp inode. If they already hold a dirty transaction and both ILOCKs, they call the reserve variant; otherwise they let the alloc variant estimate resources, allocate a transaction, and lock both inodes. The final contents call swaps mappings and, when requested, file sizes.

State and persistence: the header declares persistent repair operations but only under `CONFIG_XFS_ONLINE_REPAIR`. When repair is disabled the interface is absent, forcing callers to compile only in repair-enabled paths. Dependencies include `struct xfs_scrub`, exchmaps request definitions, fork identifiers, file offsets, and block counts.

Risks and test signals: correctness depends on callers satisfying lock/transaction preconditions from `tempfile.c`. Header drift with the implementation can break repair modules at build time. Tests should compile repair-enabled and repair-disabled configs and run repairs that use both existing-transaction reservation and fresh transaction allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempexch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.c

Purpose: implements hidden temporary inode support for online repair. Repair code uses these unlinkable inodes to stage rebuilt metadata safely, reserve/lock resources, copy generated data into mapped blocks, atomically exchange mappings with the target file, and identify/release temporary files.

Important APIs and functions: `xrep_tempfile_create()` creates an unlinkable tmpfile/symlink/directory under the root inode, root-owned and `S_PRIVATE`, puts it on the unlinked list, initializes directory or symlink contents as needed, and releases initial locks. `xrep_tempfile_adjust_directory_tree()` and `xrep_tempfile_remove_metadir()` convert temp files to/from metadata-directory accounting when the scrub target is a metadir file. Lock helpers manage temp IOLOCK/ILOCK acquisition, including polled nowait variants and two-inode locking. `xrep_tempfile_prealloc()` ensures a range is backed by written extents. `xrep_tempfile_copyin()` writes generated metadata blocks through buffer-cache buffers with periodic delwri flush. `xrep_tempfile_set_isize()`, `xrep_tempfile_roll_trans()`, and `xrep_tempfile_copyout_local()` update size/transactions/local forks. `xrep_tempexch_*()` prepares, estimates, reserves quota, allocates transactions, and executes mapping exchanges. `xrep_is_tempfile()` identifies repair temp inodes.

Control flow: temp creation first allocates root-owned dquots, chooses create/mkdir transaction reservations, allocates and initializes the inode, clears realtime inheritance, marks the VFS inode private, optionally initializes directory contents or a dummy symlink target, attaches dquots, unlinks the inode for automatic purge, commits, and finishes VFS inode setup. During repair, callers lock temp and target inodes according to helper preconditions, preallocate blocks, copy generated data one filesystem block at a time into mapped buffers, set sizes, estimate exchange resources, reserve quota for both inodes if needed, execute `xfs_exchange_mappings`, finish deferred work, and adjust incore sizes if the exchange swapped sizes. Release unwinds leftover locks, removes metadir state, and drops the inode reference.

State and persistence: tempfiles are persistent XFS inodes while repair runs but are unlinkable and recoverable through the unlinked list if repair fails before exchange. Staged metadata only replaces live metadata through atomic mapping exchange or local-fork copyout. Quota accounting is deliberately adjusted for root-owned regular temp files and metadir temp files. `S_PRIVATE`/`IOP_XATTR` and, for metadir temp files, `XFS_IRECOVERY`, distinguish private repair files from normal metadata files.

Dependencies and integration points: depends on inode creation/allocation, quota, directory initialization, symlink write helpers, bmap read/write/convert, deferred operation finishing, exchrange/exchmaps estimation and execution, metadir flags, transaction rolling, buffer delayed write submission, and scrub repair tracing. It is used by symlink, rtsummary, and other file-based metadata repairers.

Risks and test signals: risks include leaking temp inodes or locks on error paths, quota/accounting mismatches when converting metadir state, deadlocks from lock-order mistakes, under-reserving exchmaps or local-fork conversion resources, stale incore sizes after size-swapping exchanges, and partial copyin buffer flush failures. Tests should cover creation/release for regular, directory, and symlink tempfiles; shutdown/read-only rejection; metadir adjustment; prealloc conversion from holes/unwritten extents; copyin writeback errors; local fork copyout; quota-on/off exchange; and crash recovery before and after exchange.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.h

Purpose: declares the repair temporary-file helper interface and provides no-op fallbacks needed by non-repair builds.

Important APIs and types: repair-enabled declarations cover temp inode creation/release, metadir tree adjustment, temp IOLOCK/ILOCK helpers, two-inode locking helpers, preallocation, block copyin callback type `xrep_tempfile_copyin_fn`, temp file copyin, size setting, transaction rolling, local-fork copyout, and tempfile identification. The callback type lets repair modules fill each mapped temp buffer with metadata-specific content while `tempfile.c` owns block mapping and writeback.

Control flow: callers create a tempfile during setup, use lock helpers while staging or exchanging content, and rely on dispatcher teardown to call `xrep_tempfile_rele()`. For non-repair builds, `xrep_tempfile_iolock_both()` simply locks the scrub target and `xrep_tempfile_adjust_directory_tree()`/`xrep_tempfile_rele()`/`xrep_is_tempfile()` collapse to no-op or false.

State and persistence: the header only declares operations; the implementation owns hidden inode state in `sc->tempip` and `sc->temp_ilock_flags`. Dependencies include `CONFIG_XFS_ONLINE_REPAIR`, `struct xfs_scrub`, XFS fork identifiers, file/block offset types, buffer pointers, and inode types.

Risks and test signals: the interface is lock-state sensitive, so signature or precondition changes must be reflected in all repair modules. Non-repair fallback behavior must remain sufficient for shared scrub code that compiles without repair. Test signals are compile coverage for repair-disabled builds and repairs that exercise create, prealloc, copyin, set-isize, exchange, local copyout, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/trace.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/trace.c

Purpose: instantiates the XFS scrub tracepoint definitions and provides helper code used by trace event field encoders.

Important APIs and functions: `xchk_btree_cur_fsbno()` converts a btree cursor level into a filesystem block number for trace output, using the buffer at that cursor level when present or the inode root block for inode-rooted btrees. The file then defines `CREATE_TRACE_POINTS` and includes `scrub/trace.h`, causing all trace events declared in the header to be emitted in this compilation unit.

Control flow: normal scrub/repair code calls generated `trace_xchk_*`, `trace_xrep_*`, `trace_xfile_*`, `trace_xfarray_*`, and related functions. Those generated functions are materialized because this file includes `trace.h` after defining helpers and `CREATE_TRACE_POINTS`. The helper can return `NULLFSBLOCK` when the cursor level has no buffer/root block representation.

State and persistence: there is no persistent filesystem state. Runtime state is trace event emission to ftrace/perf infrastructure. Dependencies include many XFS metadata headers so trace event formatters can dereference types for scrub state, xfiles, arrays, quotas, scans, counters, orphanage, blobs, dirtree, realtime groups, and parent pointers.

Risks and test signals: trace headers are compile-sensitive because generated tracepoint code depends on every field/type referenced in `trace.h`. The helper must not dereference absent btree buffers or invalid levels. Test signals are build coverage with tracing enabled, boot/runtime enabling of representative scrub tracepoints, and event-format validation for btree cursor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/trace.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/trace.h

Purpose: declares the tracepoint surface for XFS online scrub, repair, xfile-backed data structures, live-update scans, directory tree checking, realtime metadata, and many repair subroutines. It turns internal scrub state transitions and errors into structured ftrace events.

Important APIs and types: the header sets `TRACE_SYSTEM xfs_scrub`, forward-declares scrub helper types, defines enum-to-string mappings for scrub types, flags, state flags, reference-count domains, rmap operations, directory path outcomes, and many repair-specific values. It declares reusable `DECLARE_EVENT_CLASS` templates and `DEFINE_EVENT` instances for scrub lifecycle (`xchk_start`, `xchk_done`, `xrep_attempt`, `xrep_done`), fs hook gates, scrub vectors, operation/file/block/inode/fblock errors, dquot iteration, btree operations and records, xrefs, fs counters, xfiles, xfarrays, realtime summary records, inode scans, nlink collection, parent/directory tree paths, metadata paths, repair extents, tempfile operations, symlink salvage, exchange/reap operations, and more.

Control flow: trace consumers see events emitted from scrub setup/check/repair paths, xfile/xfarray helpers, stats-sensitive sort paths, and repair side effects. Event classes encode common fields such as device, scrub type, inode, generation, AG/rtgroup, file offsets, flags, error codes, btree level, block owner, quota ids, or path outcomes. `TRACE_DEFINE_ENUM` keeps symbolic values visible to tracing tools, and the bottom include guard pattern pulls in `<trace/define_trace.h>` to generate declarations for normal includers while `trace.c` instantiates them.

State and persistence: tracepoints do not change filesystem state, but they expose transient kernel state for diagnosis. Many events read fields from live `struct xfs_scrub`, btree cursors, inodes, buffers, xfiles, arrays, and repair records, so event definitions must avoid unsafe dereferences and keep data small enough for trace buffers. Dependencies are intentionally broad because this header is the central observability contract for the scrub subsystem.

Integration points: every scrub/repair module can include this header to emit typed trace events without depending on ftrace internals. Debuggers, xfstests, perf/ftrace scripts, and maintainers can correlate scrub ioctl requests, retries, corruption reports, repair attempts, temp-file writes, exchange/reap work, and xfile/xfarray memory behavior. The enum/string mappings should stay synchronized with `xfs_scrub.h`, `scrub.c` dispatch, stats naming, and any new scrub state flags.

Risks and test signals: trace headers frequently fail as build regressions when struct fields move, enum values are added without string mappings, or a trace event is referenced in a config where its type is unavailable. Overly expensive trace arguments can perturb hot scrub loops. Test signals include allmodconfig-style builds, enabling tracepoints during symlink/rtsummary repair, verifying event formats under `/sys/kernel/tracing/events/xfs_scrub`, and ensuring new scrub types have trace enum strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.c

Purpose: implements `xfarray`, a pageable xfile-backed array for large numbers of fixed-size scrub/repair records. It trades direct memory access for lower reclaim pressure by storing records in shmem-backed xfiles, supports sparse/unset entries, and provides an interruptible external sort optimized for xfile folios.

Important APIs and functions: `xfarray_create()` creates an xfile, allocates the array plus one-record scratch buffer, records object size/log2, and caps maximum record count. `xfarray_load()`, `xfarray_store()`, `xfarray_unset()`, `xfarray_store_anywhere()`, `xfarray_load_next()`, `xfarray_length()`, `xfarray_bytes()`, and `xfarray_truncate()` provide fixed-record storage, sparse iteration, and accounting. Sorting helpers include `xfarray_sortinfo_alloc()`, `xfarray_isort()`, `xfarray_foliosort()`, `xfarray_qsort_pivot()`, `xfarray_sort_scan()`, `xfarray_qsort_push()`, and the public `xfarray_sort()`.

Control flow: records are addressed by converting array indexes to xfile offsets with a shift when the object size is a power of two or division otherwise. Stores reject indexes beyond `max_nr` and assert that all-zero records are not stored as real data. Unset of the last record shrinks `nr`; unset of an interior record writes zeroes and increments `unset_slots`. Iteration uses `xfile_seek_data()` near page boundaries to avoid instantiating holes, then skips all-zero records. Sorting uses an explicit-stack quicksort for large ranges, median-of-nine pivot selection, smaller-partition-first stack management, heapsort for small ranges, direct folio sorting when a partition fits in one xfile folio, and cached folio scanning while partitioning. Long sorts call scrub relaxation and can be made killable by flags.

State and persistence: xfarray state is process/kernel memory backed by an xfile; it is not on-disk XFS metadata. Persistent-looking offsets live only for the lifetime of the array. `nr`, `max_nr`, `unset_slots`, `obj_size`, and `obj_size_log` track logical array state; the xfile page cache stores record bytes and can be discarded on truncate. Sorting allocates transient `xfarray_sortinfo` with partition stacks, pivot/scratch storage, optional cached folio, and debug counters.

Dependencies and integration points: depends on scrub allocation/relax helpers, xfile load/store/seek/get-folio/put-folio/discard/bytes APIs, kernel `sort()`, folio APIs, tracepoints, and callers in scrub repair modules that need scalable record collection and sorting. `xfarray.h` exposes the iteration/sort contract and `xfarray_cmp_fn` comparison callback type.

Risks and test signals: risks include object-size boundary errors, interpreting legitimate all-zero records as unset, stale `unset_slots` after `store_anywhere`, sparse iteration accidentally instantiating holes, qsort stack-depth bugs, bad median sampling with sparse arrays, signal interrupt semantics, and direct folio sorting of records crossing folio boundaries. Tests should cover non-power-of-two record sizes, max-capacity failures, append/store/load/unset/store-anywhere behavior, sparse load-next iteration, truncate reset, sort correctness for small/large/already-sorted/reverse/duplicate records, killable sort termination, and xfile byte accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.h

Purpose: declares the xfile-backed fixed-record array abstraction and its sort interface for scrub and repair modules that need large, pageable, mostly sequential collections.

Important APIs and types: `xfarray_idx_t` is a 64-bit index with `XFARRAY_NULLIDX` and `XFARRAY_CURSOR_INIT` sentinels. `struct xfarray` exposes backing `xfile`, logical length, max length, unset-slot count, object size, and object-size log. Public functions create/destroy arrays, load/store/unset elements, store into any unset slot, test for all-zero/null records, truncate, report backing bytes, get length, and load the next non-null entry. Inline helpers implement sparse load, append, and `xfarray_iter()` returning 1/0/errno. Sorting declarations include `xfarray_cmp_fn`, small-sort and pivot constants, `struct xfarray_sortinfo`, `XFARRAY_SORT_KILLABLE`, and `xfarray_sort()`.

Control flow: callers create an array with a required capacity and record size, append or store nonzero records, optionally use unset/store-anywhere for sparse lifecycle management, iterate with a cursor initialized to `XFARRAY_CURSOR_INIT`, and sort with a comparison function. The sortinfo structure documents its variable-sized tail allocation for quicksort low/high stacks and scratch/pivot records.

State and persistence: the header documents logical state stored in the implementation: backing xfile pages, `nr`, `max_nr`, `unset_slots`, and sort scratch/folio cache. Data is transient scrub working state, not filesystem metadata. All-zero records are reserved as the unset marker, which is a key contract for callers.

Dependencies and integration points: depends on `struct xfile`, scrub relaxation state, kernel comparison function type, and xfile-backed callers such as btree rebuilders, parent/directory scans, nlinks, counters, and other repair collectors. It hides xfile offset math from callers while allowing them to monitor bytes and sort records.

Risks and test signals: callers that need to store all-zero records must encode them differently or they will disappear during iteration. Because the header exposes struct fields, external users can accidentally mutate invariants. Test signals should include compile coverage for all inline helpers, sparse iteration API return values, sort flag behavior, and consumers that rely on `unset_slots` or `xfarray_bytes()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.c

Purpose: implements append-only variable-length blob storage on top of xfiles for scrub/repair code that needs to keep names or other variable-sized records and refer to them by opaque cookies.

Important APIs and functions: `struct xb_key` is the packed on-xfile header containing magic, blob size, and self offset. `xfblob_create()` creates the backing xfile and initializes `last_offset` to `PAGE_SIZE`, leaving the first page unused as a guard against null/zero cookies. `xfblob_store()` writes a key header and blob bytes, returns the starting offset as an `xfblob_cookie`, and advances `last_offset`. `xfblob_load()` validates the key magic/self-offset and reads the blob into a caller buffer. `xfblob_free()` validates and discards one stored blob. `xfblob_bytes()` and `xfblob_truncate()` report backing storage and reset to the initial offset.

Control flow: stores append sequentially: write header at `last_offset`, write payload after the header, publish cookie, then advance. If payload write fails, only the header range is discarded. Loads and frees first read the header from the cookie and reject stale/corrupt cookies with `-ENODATA`; loads also reject too-small destination buffers with `-EFBIG`.

State and persistence: blob data is transient xfile-backed memory, not durable filesystem metadata. `last_offset` is the only allocator state and there is no reuse of freed interior holes; truncate discards everything after the first page and resets append position. The key header adds lightweight integrity checking so callers can detect invalid cookies.

Dependencies and integration points: depends on xfile create/load/store/discard/bytes, scrub allocation flags, and `xfblob.h` name helpers for storing `struct xfs_name` strings. It complements `xfarray`: arrays can store fixed records containing blob cookies when variable-length names are needed elsewhere.

Risks and test signals: risks include unbounded growth without reuse, partial store cleanup discarding only the key header and leaving a failed partial payload to xfile behavior, no concurrency control around `last_offset`, size/cookie truncation bugs, and callers passing undersized buffers. Tests should cover create/destroy, store/load/free/truncate, invalid cookie magic/offset, load buffer too small, repeated frees, byte accounting, and storing names through the inline helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.h

Purpose: declares the xfile-backed variable-length blob storage interface and convenience helpers for storing XFS names.

Important APIs and types: `struct xfblob` contains the backing xfile and next append offset. `xfblob_cookie` is a `loff_t` offset returned by stores and later used for loads/frees. Public functions create/destroy blob stores, load/store/free blobs, query backing bytes, and truncate all blobs. `xfblob_storename()` stores `xfs_name->name` with `xfs_name->len`; `xfblob_loadname()` loads bytes into `xfs_name->name` and restores the length.

Control flow: callers create a blob store, append payloads to receive cookies, embed those cookies in other scrub records, later load or free blobs by cookie, and finally truncate or destroy the store. The name helpers reduce duplicated casting and length assignment in directory/parent-pointer scrub code.

State and persistence: state is transient and xfile-backed. Cookies are only meaningful for the lifetime of the `xfblob` and after a truncate all previous cookies become stale. The header exposes fields, so callers can inspect but should not mutate allocator state directly.

Dependencies and integration points: depends on `struct xfile`, `struct xfs_name`, and the implementation's header validation. It is commonly paired with `xfarray` records that need stable references to variable-length names.

Risks and test signals: risks include callers treating cookies as durable IDs, reusing cookies after truncate/free, insufficient destination storage in `xfblob_loadname()`, and direct mutation of `last_offset`. Test signals should exercise the generic blob API and name-specific helpers with maximum-length names and stale cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.h -->
