# subset-b-005789 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.c

Purpose: Implements online-repair support for finding and confirming the parent directory of a target directory. It provides a brute-force filesystem directory scan, a live directory-update hook to keep scan results coherent while the filesystem changes, and shortcuts for root, metadata-root, unlinked directories, and dcache-derived parents.

Important APIs, types, and functions: The internal `struct xrep_findparent_info` tracks the directory currently being scanned, scrub context, optional parent-scan state, found parent inode, and whether that result is tentative. Public functions are `__xrep_findparent_scan_start()`, `xrep_findparent_scan()`, `xrep_findparent_scan_teardown()`, `xrep_findparent_scan_finish_early()`, `xrep_findparent_confirm()`, `xrep_findparent_self_reference()`, and `xrep_findparent_from_dcache()`. Key callbacks are `xrep_findparent_dirent()`, `xrep_findparent_walk_directory()`, and `xrep_findparent_live_update()`.

Control flow: Scan setup validates dirent fsgates, initializes an `xchk_iscan`, and registers an `xfs_dir_hook`. `xrep_findparent_scan()` iterates live inodes, walks only directory inodes, marks each visited inode, and releases references. Directory walking skips the target itself, scrub temporary inodes, metadata-vs-regular tree mismatches, sick directories, and zapped directories before calling `xchk_dir_walk()`. Dirent callbacks accept only non-dot entries whose target inode equals `sc->ip->i_ino`; a second conflicting parent returns `-EFSCORRUPTED`. The live update hook adjusts the stored parent when an already-visited directory gains or loses a child entry for the target.

State and persistence: This file writes no durable metadata directly. It maintains transient scan state in `xrep_parent_scan_info`, protected by its mutex, and relies on inode locks plus the iscan visited cursor to decide when live updates must be replayed. The confirmed or discovered parent inode number is consumed by higher-level directory or parent-pointer repair code.

Dependencies and integration points: Depends on XFS directory walking, dirent hooks, live inode scan, dcache alias lookup, inode health flags, repair tempfile detection, metadata directory classification, tracepoints, and scrub termination handling. It integrates with repair callers that need a reliable parent before fixing dotdot or parent pointer state.

Risks and test signals: Risk centers on races between full-tree scans and concurrent renames, missing live updates for skipped or already-scanned directories, accepting a corrupt directory as authoritative, and confusing metadata-tree parents with normal directory parents. Test with concurrent rename/link/unlink while repairing dotdot, duplicate parent dirents, zapped or sick directories, metadata directory trees, unlinked directories, root/metadir roots, dcache-only parent hints, termination requests, and parent candidates that are invalid, non-directory, or self-referential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.h

Purpose: Declares the parent-directory scan state and public helper API used by XFS online repair to discover, confirm, and publish a directory parent.

Important APIs, types, and functions: `struct xrep_parent_scan_info` stores the scrub context, embedded `xchk_iscan`, dirent hook, mutex, discovered `parent_ino`, and a `lookup_parent` flag. It declares scan lifecycle functions, confirmation helpers, dcache/self-reference shortcuts, and the inline `xrep_findparent_scan_found()` setter.

Control flow: Callers initialize the structure with `xrep_findparent_scan_start()` or `__xrep_findparent_scan_start()` when they need a custom notifier. `xrep_findparent_scan_found()` serializes parent updates through `pscan->lock`, allowing directory-update hooks and scan code to publish changes safely. Callers then scan, optionally finish early, and tear down hooks and iscan state.

State and persistence: All state is transient and in-memory. The only shared mutable field is `parent_ino`, guarded by the embedded mutex. No on-disk update is performed by this header.

Dependencies and integration points: Exposes `xchk_iscan`, `xfs_dir_hook`, `xfs_scrub`, and notifier integration to directory, parent-pointer, and repair code. The API assumes callers follow the locking contract documented in `findparent.c`.

Risks and test signals: Incorrect lifecycle ordering can leave dirent hooks registered or destroy the mutex while updates are possible. Test repeated start/scan/finish/teardown, early-finish paths, custom hook registration, concurrent updates to `parent_ino`, and callers reading the result only while holding the required inode locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/findparent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fsb_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fsb_bitmap.h

Purpose: Provides a type-specific wrapper around `xbitmap64` for sets of filesystem block numbers (`xfs_fsblock_t`).

Important APIs, types, and functions: Defines `struct xfsb_bitmap` containing `struct xbitmap64 fsbitmap`, plus inline helpers `xfsb_bitmap_init()`, `xfsb_bitmap_destroy()`, `xfsb_bitmap_set()`, and `xfsb_bitmap_walk()`.

Control flow: Users initialize the bitmap, add fsblock ranges with a start and length, iterate merged ranges through an `xbitmap64_walk_fn`, and destroy backing state when done. The wrapper does not add policy beyond type-directed naming.

State and persistence: State is an in-memory interval bitmap. Nothing is persisted; callers use it to stage scrub or repair observations before later action.

Dependencies and integration points: Depends on the generic scrub bitmap implementation and XFS block typedefs. It is intended for repair/scrub code that wants compile-time clarity between fsblock and other address spaces.

Risks and test signals: Main risks are unit mixups at call sites and missed destruction on error paths. Test range insertion/merge, walk ordering, empty walks, allocation failures from the underlying bitmap, and users that translate between AG blocks and fsblocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fsb_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.c

Purpose: Scrubs XFS filesystem summary counters by independently aggregating per-AG inode/free-space state and realtime free extents, then comparing those expected values with in-core percpu counters.

Important APIs, types, and functions: Exports `xchk_setup_fscounters()` and `xchk_fscounters()`. Important helpers include `xchk_fscount_warmup()`, `xchk_fscounters_freeze()`, `xchk_fscounters_cleanup()`, `xchk_fscount_btreeblks()`, `xchk_fscount_aggregate_agcounts()`, `xchk_fscount_count_frextents()`, and `xchk_fscount_within_range()`. `XCHK_FSCOUNT_MIN_VARIANCE` defines minimum tolerance for unfrozen scans.

Control flow: Setup optionally enables drain gates for pre-lazysbcount filesystems, allocates `xchk_fscounters`, computes valid inode-count bounds, initializes per-AG state by reading AGI/AGF headers, and freezes the filesystem for repair or try-harder scans. The scrub function snapshots global counters, rejects impossible negative or out-of-range values, aggregates initialized per-AG counters, subtracts per-AG and global reservations plus delayed allocation counters, optionally counts realtime bitmap free extents, and compares expected values against before/after counter sums. Unfrozen mismatches return `-EDEADLOCK` so userspace can retry with stronger freeze permission; frozen mismatches are marked corrupt.

State and persistence: The scrub stores computed expected counters, valid inode ranges, realtime-delalloc adjustment, and freeze state in `sc->buf`. It does not update persistent counters; repair uses the computed state. The freeze cleanup callback thaws the filesystem and logs an emergency if thaw fails.

Dependencies and integration points: Depends on superblock freeze/thaw, mount write protection, percpu counters, per-AG cached AGI/AGF fields, btree block counting for old filesystems, realtime bitmap queries, delayed allocation counters, and scrub error/incomplete handling. It feeds `fscounters_repair.c`.

Risks and test signals: Race tolerance is subtle: lockless aggregation can be perturbed by allocation, inodegc, delayed allocation, and realtime reservations. Test idle and high-churn filesystems, repair with frozen fs, pre-lazysbcount btree-block counting, negative transient free counters, realtime and zoned configurations, per-AG reservation accounting, malformed initialized flags, counter overflow bounds, and retry behavior that sets incomplete instead of repairing from partial data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.h

Purpose: Defines the shared in-memory state used by filesystem summary counter scrub and repair.

Important APIs, types, and functions: `struct xchk_fscounters` records the scrub context, computed `icount`, `ifree`, `fdblocks`, `frextents`, delayed realtime extent reservations, valid inode-count bounds, and whether scrub froze the filesystem.

Control flow: `xchk_setup_fscounters()` allocates and initializes this structure; `xchk_fscounters()` fills the computed fields; `xrep_fscounters()` consumes them to reset global counters. The `frozen` bit controls strictness and cleanup.

State and persistence: The structure is transient `sc->buf` state. It mirrors values that may later be written to in-core counters and, for non-rtgroup realtime free extents, superblock state by repair.

Dependencies and integration points: Included by both scrub and repair implementations. It couples the checker and repairer, so field semantics must remain consistent across both files.

Risks and test signals: Stale or incomplete values can cause bad repairs if the incomplete flag is missed. Test setup failure cleanup, frozen and unfrozen paths, realtime delayed-reservation subtraction, and repair refusing to run when `frozen` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters_repair.c

Purpose: Repairs filesystem summary counters by resetting the in-core counters to the values computed during the mandatory scrub phase.

Important APIs, types, and functions: Exports `xrep_fscounters()`, which consumes `struct xchk_fscounters` from `sc->buf` and updates `m_icount`, `m_ifree`, `XC_FREE_BLOCKS`, `XC_FREE_RTEXTENTS`, and sometimes `sb_frextents`.

Control flow: Repair first asserts that the filesystem was frozen during scrub and refuses to proceed otherwise. It then sets inode and free-block percpu counters to scrubbed values. Realtime free extents are adjusted by subtracting delayed realtime reservations for the in-core freecounter; on non-rtgroup realtime filesystems it also updates `mp->m_sb.sb_frextents`.

State and persistence: The direct writes are to in-memory counters and the mounted superblock copy. Online repair relies on v5 lazy superblock counters for data block persistence, while realtime free extent handling still needs explicit superblock-state correction on configurations without rtgroups.

Dependencies and integration points: Depends on `fscounters.c` for accurate computed values and freeze ownership, on XFS freecounter helpers, realtime/zoned feature predicates, and scrub tracepoints. It is invoked by the scrub/repair framework only after a corrupt counter finding.

Risks and test signals: The high-risk path is repairing from unfrozen or incomplete observations; the code guards this with `frozen`. Test repair after clean frozen aggregation, refusal without freeze, realtime with delayed allocations, zoned filesystems skipping frextents, rtgroup vs non-rtgroup superblock updates, and post-repair rescrub equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/health.c

Purpose: Maps scrub results to XFS in-core health state, clearing or setting sick flags for filesystem, allocation group, realtime group, and inode metadata after scrub and repair.

Important APIs, types, and functions: Defines `enum xchk_health_group`, `struct xchk_health_map`, and `type_to_health_flag[]`, mapping scrub types to health groups and sick masks. Public functions include `xchk_health_mask_for_scrub_type()`, `xchk_update_health()`, `xchk_ag_btree_del_cursor_if_sick()`, `xchk_mark_healthy_if_clean()`, `xchk_file_looks_zapped()`, and `xchk_health_record()`.

Control flow: `xchk_update_health()` handles the special HEALTHY scrub type, determines whether scrub found direct or cross-reference corruption, merges `healthy_mask` when clean, and updates the target group. Inode repairs add `XFS_SICK_INO_FORGET` so sickness does not survive inode inactivation incorrectly. `xchk_ag_btree_del_cursor_if_sick()` drops cross-reference btree cursors if the referenced structure is already known sick, except when that structure is the primary scrub target or was just repaired. `xchk_health_record()` scans fs, AG, and realtime group health for lingering primary sickness.

State and persistence: Health flags are in-core state associated with mount, perag/rtgroup objects, and inodes. The file does not write on-disk metadata, but it changes what future scrub and health reporting believe is sick, healthy, zapped, or too unreliable for cross-reference.

Dependencies and integration points: Depends on `xfs_health` APIs, scrub type constants, btree cursor sick masks, perag/rtgroup iteration, and scrub output flags. It gates cross-reference behavior throughout scrub and records repair effectiveness after rescrub.

Risks and test signals: Incorrect mapping can hide corruption or keep fixed metadata marked sick. Test every scrub type mapping, clean vs corrupt vs xcorrupt outcomes, HEALTHY full-fs clearing, already-fixed AG repairs, inode inactivation during repair, cursor deletion for sick xref btrees, zapped-file detection, and health-record scans over AG and realtime group primary flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/health.h

Purpose: Declares the scrub health-state interface used to map scrub outcomes to XFS sick/healthy flags and cross-reference gating.

Important APIs, types, and functions: Declares `xchk_health_mask_for_scrub_type()`, `xchk_update_health()`, `xchk_ag_btree_del_cursor_if_sick()`, `xchk_mark_healthy_if_clean()`, `xchk_file_looks_zapped()`, and `xchk_health_record()`.

Control flow: Scrub setup and teardown code query masks, scrub runners call `xchk_update_health()` after checks and repairs, and cross-reference setup calls `xchk_ag_btree_del_cursor_if_sick()` to avoid trusting known-bad secondary structures.

State and persistence: No state is defined in the header. It exposes operations that mutate in-core health state but not durable metadata.

Dependencies and integration points: Depends on `struct xfs_scrub` and btree cursors. It is a shared boundary between scrub implementations, repair code, and XFS health reporting.

Risks and test signals: Prototype drift or misuse can cause health flags to be updated at the wrong time. Test build coverage for all scrub types and runtime cases where repair changes `sick_mask` before final health update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc.c

Purpose: Scrubs the inode allocation btrees, validating inobt and finobt records against inode cluster buffers, each other, free-space ownership, and reverse mappings.

Important APIs, types, and functions: Exports `xchk_setup_ag_iallocbt()`, `xchk_iallocbt()`, `xchk_xref_is_not_inode_chunk()`, and `xchk_xref_is_inode_chunk()`. Internal state `struct xchk_iallocbt` tracks seen inode count and expected record sequencing. Key helpers include finobt/inobt xref routines, chunk checks, cluster buffer checks, record alignment validation, rmap btree block and inode extent xrefs, and `xchk_xref_inode_check()`.

Control flow: Setup enables intent draining when needed and initializes AG btree scrub. The record callback decodes each inobt/finobt record, validates record contents, alignment, sparse hole/free masks, inode counts, and cluster-level consistency. Cluster checking maps inode buffers directly, verifies dinode magic and inode numbers, compares btree free bits with incore allocation state or disk `di_mode`, and may request try-harder retry if unfrozen state is ambiguous. Cross-reference paths compare inobt and finobt free/hole state, ensure inode chunks are used space and only owned by inode rmap records, and compare total btree/inode block counts with rmap ownership.

State and persistence: Scrub maintains only transient counters and sequencing expectations. It does not repair or persist changes; corruption is reported through scrub flags and btree cursor state.

Dependencies and integration points: Depends on XFS btree scrub framework, inode allocation btree helpers, inode cache allocation queries, inode buffer mapping, AG headers, rmap/refcount/COW xrefs, sparse inode geometry, and health-driven cross-reference skipping. Repair is handled by `ialloc_repair.c`.

Risks and test signals: Subtle risks include sparse inode holemask interpretation, geometries where one inode chunk spans clusters or one cluster spans chunks, racing inode allocation/free, stale finobt records, and rmap count disagreement. Test sparse and non-sparse filesystems, large block-size inode chunk layouts, all-free/all-allocated finobt omission rules, corrupt inode magic/di_ino, missing or extra rmap ownership, shared/COW staging overlap, pre-try-harder deadlock retries, and both INOBT and FINOBT scrub directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc_repair.c

Purpose: Rebuilds both inode allocation btrees for an AG from reverse-mapping records and inode cluster contents.

Important APIs, types, and functions: `struct xrep_ibt` tracks the reconstructed record under construction, staged new inobt/finobt (`xrep_newbt`), old inode btree blocks, an `xfarray` of inode records, inode/free counts, finobt record count, and array cursor. Public functions are `xrep_iallocbt()` and `xrep_revalidate_iallocbt()`. Core helpers process rmap records, read inode clusters, construct free/hole masks, bulk-load staged btrees, reset AGI counters, reap old btree blocks, and revalidate.

Control flow: Repair requires rmapbt. It allocates an xfarray sized for maximum AG inode records, scans all AG rmaps for `OWN_INODES` and `OWN_INOBT`, records old btree blocks for later reaping, validates inode extents against geometry and free-space btrees, reads each inode cluster directly, derives in-use state from incore inode allocation or disk dinode mode, and appends normalized inobt records. It then checks record ordering, uses `xrep_newbt` and btree bulk loading to stage new inobt and finobt roots, commits staged roots into the AGI, recalculates AGI counts and perag state, commits unused newbt reservations, rolls the AG transaction, and reaps old inode-btree blocks.

State and persistence: New btree blocks are allocated and tracked with autoreap until committed. The durable change is replacement of AGI btree roots and levels plus AGI inode/free counters; old btree blocks are freed after the new roots are logged. Repair also forces filesystem summary counter recalculation and may request per-AG reservation reset for finobt.

Dependencies and integration points: Depends on rmapbt correctness, free-space btrees, inode cluster buffer reads, sparse inode geometry, `xfarray`, `xagb_bitmap`, btree staging/bulk-load APIs, `newbt.c`, reap helpers, AG transaction rolling, and health masks for both INOBT and FINOBT.

Risks and test signals: Risks include rebuilding from corrupt rmap data, losing old btree blocks before new roots are durable, wrong free/hole mask derivation from uncached inodes, finobt record filtering, block reservation ENOSPC, and geometries with sparse or multi-record clusters. Test rmap-less refusal, dense and sparse inode AGs, corrupt inode extent alignment, all-free/all-used chunks, finobt disabled/enabled with reservations, ENOSPC mid-build cancellation, crash after staged root commit but before reaping, summary counter recalculation, and post-repair revalidation of both btrees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ino_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/ino_bitmap.h

Purpose: Provides a type-specific bitmap wrapper for individual XFS inode numbers.

Important APIs, types, and functions: Defines `struct xino_bitmap` around `struct xbitmap64`, with inline `xino_bitmap_init()`, `xino_bitmap_destroy()`, `xino_bitmap_set()`, and `xino_bitmap_test()`.

Control flow: Callers initialize the bitmap, add single inode numbers as one-length ranges, query membership with `xino_bitmap_test()`, and destroy the backing bitmap. The test helper uses a one-entry length to ask the generic bitmap whether the inode is covered.

State and persistence: Maintains transient in-memory inode membership only. No on-disk metadata is changed.

Dependencies and integration points: Depends on generic `xbitmap64` and XFS inode number types. It is useful to scrub/repair code that tracks visited, affected, or staged inode sets without mixing address spaces.

Risks and test signals: Watch for allocation failures from `xbitmap64_set`, false positives from range merging, and omitted destruction. Test single insert/test, absent inodes, adjacent inode merging, large inode numbers near filesystem limits, and repeated destroy after empty initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ino_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/inode.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/inode.c

Purpose: Implements inode-core scrub: acquiring the target inode safely, validating on-disk inode fields via an incore copy, and cross-referencing inode allocation and fork counters with other metadata.

Important APIs, types, and functions: Exports `xchk_setup_inode()` and `xchk_inode()`. Important helpers include `xchk_prepare_iscrub()`, `xchk_install_handle_iscrub()`, `xchk_dinode()`, `xchk_inode_flags()`, `xchk_inode_flags2()`, `xchk_inode_extsize()`, `xchk_inode_cowextsize()`, `xchk_inode_xref_finobt()`, `xchk_inode_xref_bmap()`, `xchk_inode_xref()`, `xchk_inode_check_reflink_iflag()`, and `xchk_inode_check_unlinked()`.

Control flow: Setup handles the open file, handle-based lookup, metadata-directory restrictions, invalid inode numbers, safe untrusted iget, and fallback AGI-protected imap lookup when iget fails due to corruption. If repair is possible and the inode cannot be instantiated, setup saves the raw imap for inode repair. Scrub copies the incore inode to a disk-format dinode, validates mode, version, metatype, ids, format, timestamps, size, block counts, flags, fork offsets, attr/data formats, extent counters, extsize hints, and feature compatibility. If the core is clean, regular files get reflink-iflag verification, all inodes get unlinked-list consistency checks, and xrefs check used space, finobt state, rmap ownership, sharing/COW staging, and fork block counts.

State and persistence: Scrub itself does not persist changes. It may keep a transaction and AGI buffer in setup to preserve the evidence needed by repair when an allocated inode cannot be loaded. Findings are recorded in scrub output flags and inode-specific corrupt/warning/preen state.

Dependencies and integration points: Depends on VFS inode locking, XFS iget/imap, quota attach, transactions, inode buffer/fork validators, reflink, rmap/refcount xrefs, finobt, bmap extent counting, metadata directory policy, and `inode_repair.c` for raw-inode salvage.

Risks and test signals: Acquisition fallback is delicate because setup must distinguish free inodes, corrupt inobt, and allocated-but-unloadable inodes. Validation risks include feature-gated flags, realtime/reflink interactions, attr fork boundary math, and block count comparisons for shared extents. Test open-file and handle scrub, bad inode numbers, corrupt dinodes that fail iget, v1/v2/v3 inode fields, metadir inodes, realtime and reflink files, large extent counts, invalid timestamps, unlinked-list mismatches, finobt disagreement, and xref degradation when secondary btrees are sick.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/inode_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/inode_repair.c

Purpose: Repairs inode records enough to pass verifiers and then fixes higher-level incore inode inconsistencies such as block counts, flags, ids, timestamps, parent-pointer attr fork presence, and unlinked-list membership.

Important APIs, types, and functions: `struct xrep_inode` stores raw imap, block/extent counts from rmap scans, sick masks to set after zapping forks, ACL-zap state, and an iscan for recovering file type from dirents. Public entry points are `xrep_setup_inode()` and `xrep_inode()`. Major helper families repair raw dinode buffers (`xrep_dinode_buf_core()`, `xrep_dinode_header()`, `xrep_dinode_mode()`, `xrep_dinode_core()`), discover mode from directory ftypes, count rmap-owned extents, validate and zap data/attr forks, adjust forkoff, schedule quotacheck, and fix live inode fields.

Control flow: If scrub could not instantiate `sc->ip`, repair reads all rmapbt and realtime rmap records for the target inode, reads the inode cluster buffer directly, repairs dinode buffer verifier fields, normalizes header, tries to recover a plausible mode by scanning directories, clears or adjusts invalid flags, sizes, hints, and fork data, logs the raw dinode, retries iget while still protected, commits the raw repair, attaches dquots, and marks any zapped inode subsystems sick. Once an incore inode exists, repair joins it to a transaction, recomputes data and attr block/extent counters from bmap walks, ensures extent-count width, creates an attr fork when parent pointers require it, clamps timestamps, cleans incompatible flags and ids, fixes directory sizes, clears bad extsize hints, tries to clear stale reflink flags, and reconciles unlinked-list membership.

State and persistence: Durable changes include raw inode cluster buffer updates, inode core field logging, possible attr-fork creation, unlinked-list updates, and deferred extent work. Repair can intentionally zap unrecoverable data or attr fork metadata to make later bmap/dir/attr repairs possible; it records zapped sickness flags and forces quota checks when identity or severe inode damage could invalidate accounting.

Dependencies and integration points: Depends on rmapbt/rtrmapbt for salvage counts, directory walking and live iscan for ftype inference, inode buffer and fork verifier rules, bmap extent counting, quota repair hooks, parent pointer support, reflink helpers, realtime group cursors, transactions, and scrub health state. It is sequenced before specialized fork, directory, symlink, xattr, and bmap repairs that may rebuild zapped structures.

Risks and test signals: This is a high-blast-radius repair path because it makes conservative security decisions and can discard unverifiable fork metadata. Test unloadable corrupt dinodes, invalid mode recovery from one or multiple dirents, busy iscan retry behavior, rmap-less refusal, mixed data and realtime extents, corrupt btree roots in forks, attr fork zapping and ACL lockdown, parent-pointer attr fork creation, quota-check forcing, setuid/setgid stripping after id resets, directory/symlink zero-size repair, stale reflink flag clearing, unlinked-list insertion/removal, crash after raw-dinode commit, and follow-up bmap/dir/attr repair signals for zapped forks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/inode_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.c

Purpose: Provides a live inode scanner for online scrub/repair tasks that must walk all allocated inodes while concurrent allocation, deletion, and metadata updates continue.

Important APIs, types, and functions: Exports `xchk_iscan_start()`, `xchk_iscan_finish_early()`, `xchk_iscan_iter()`, `xchk_iscan_iter_finish()`, `xchk_iscan_teardown()`, `xchk_iscan_mark_visited()`, and `xchk_iscan_want_live_update()`. Internal helpers advance through inobt records under AGI protection, batch iget up to one inode chunk, maintain skipped-inode masks, retry inodegc races, and choose a rotor start AG.

Control flow: Start chooses a rotating start inode, initializes cursor and visited state, and stores iget timeout policy. Iteration first returns already batched inodes; otherwise it advances under AGI lock to the next allocated inode, moves cursor and visited range across sparse inode address gaps, igets the first inode with no-retry/dontcache flags, optionally batches consecutive allocated inodes, and records unallocated inodes in the batch as skipped. Callers mark each inode visited after scanning under sufficient locks. `xchk_iscan_want_live_update()` tells hook code whether an inode update lies in the visited range, accounts for wraparound, and treats skipped newly allocated inodes as requiring live updates.

State and persistence: All state is transient in `struct xchk_iscan`: start/cursor/visited inode numbers, opstate bits, retry deadline, batch array, and skipped mask, guarded by a mutex for hook-visible fields. No on-disk state is modified.

Dependencies and integration points: Depends on inobt lookup, AGI locking, `xfs_iget`, inodegc push/flush, perag references, scrub transactions, and tracepoints. Used by parent finding, inode mode recovery, and any repair that builds a new live index with metadata update hooks.

Risks and test signals: Correctness depends on never missing updates for inodes already scanned or skipped during a batch. Test wraparound scans, empty AG gaps, sparse inode address spaces, trylock AGI mode under rename/AGI lock pressure, inodegc races returning ENOENT/EAGAIN, EBUSY timeout behavior, abort bit handling, batch skipping for newly allocated inodes, live-update predicates before start/after finish, and teardown releasing batched inode references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.h

Purpose: Defines the live inode scan state and API used by online scrub/repair components that need full-filesystem inode iteration plus live-update filtering.

Important APIs, types, and functions: `struct xchk_iscan` stores scrub context, mutex, scan start, next cursor, optional skip inode, last visited inode, opstate bits, iget retry settings, batch base, skipped mask, and cached inode references. Defines opstate bits `XCHK_ISCAN_OPSTATE_ABORTED` and `XCHK_ISCAN_OPSTATE_TRYLOCK_AGI`, inline abort/trylock helpers, and the iterator/lifecycle prototypes.

Control flow: Callers start a scan, optionally set abort or AGI trylock mode, call `xchk_iscan_iter()` until it returns zero or error, mark each inode visited, finish any batch, and teardown. Hook code calls `xchk_iscan_want_live_update()` while holding appropriate inode locks.

State and persistence: The header defines only in-memory scan cursor state. The mutex protects fields shared with live update hooks. Inode references stored in `__inodes[]` must be released by iterator finish or teardown.

Dependencies and integration points: Exposes XFS inode and scrub types to directory, parent, inode repair, and future index-rebuild code. Its contracts rely on AGI locks and caller-held inode locks described in `iscan.c`.

Risks and test signals: Misusing private cursor fields can break live-update correctness. Test API users for balanced start/teardown, abort propagation, skip_ino filtering, trylock mode, and no leaked batched inode references on early exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.c

Purpose: Provides a validation-oriented extended-attribute walker that calls a callback for every xattr in shortform, leaf, or node-format attr forks without cursor restarts.

Important APIs, types, and functions: Exports `xchk_xattr_walk()`. Internal helpers walk shortform entries, leaf block entries, single-leaf attr forks, find the leftmost node-format leaf, and traverse right-sibling leaf chains while detecting loops with `xdab_bitmap`.

Control flow: The public walker requires the inode ILOCK and returns immediately if the inode has no attrs. Shortform attrs are iterated from the in-core attr fork. Non-local attrs load attr fork extents, then either read block zero as a leaf or descend the dabtree to the leftmost leaf. Node traversal verifies node and leaf headers, records seen dablocks, walks leaf entries, optionally calls a leaf callback between leaves, follows `forw` sibling pointers, and rejects cycles or malformed levels. Leaf entries pass local values inline and remote values as `NULL` with the remote value length.

State and persistence: The walker only reads attr fork structures and transient buffers. It keeps an in-memory bitmap of seen dablocks for node-format loop detection and releases transaction buffers after each leaf.

Dependencies and integration points: Depends on XFS attr fork formats, attr leaf/node readers and verifiers, dab bitmap helpers, scrub transactions, and caller-provided callbacks. Used by scrub/repair code that needs deterministic xattr enumeration, including parent-pointer or attr validation.

Risks and test signals: Risks include malformed dabtrees causing loops, incorrect local vs remote value interpretation, level mismatch during descent, and walking without loaded extents or locks. Test shortform attrs, leaf local and remote entries, multi-leaf node chains, corrupt magic/header/count/level, sibling cycles, callback error propagation, remote value lengths, empty attr forks, and buffer release on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.h

Purpose: Declares callback types and the public xattr walker used by XFS scrub code.

Important APIs, types, and functions: Defines `xchk_xattr_fn` for per-attribute callbacks with flags, name, optional value pointer, value length, and private data. Defines `xchk_xattrleaf_fn` for per-leaf progress callbacks. Declares `xchk_xattr_walk()`.

Control flow: Callers provide callbacks and private state, hold the inode ILOCK, and invoke `xchk_xattr_walk()` to receive each attr entry in fork order. The leaf callback can be used for periodic processing between node-format leaf blocks.

State and persistence: No state is defined. Callback consumers own any state transitions; the walker is read-only.

Dependencies and integration points: Depends on `struct xfs_scrub` and `struct xfs_inode`. It is an integration point for attr, parent-pointer, and repair code that needs a uniform attr enumeration surface.

Risks and test signals: Callback ABI mistakes can mishandle remote values where `value == NULL`. Test consumers with local and remote attrs, namespace flags, long names/values, and callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/metapath.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/metapath.c

Purpose: Scrubs and repairs metadata-directory paths for metadir-enabled XFS filesystems, ensuring expected names under the metadata tree point to the correct incore metadata inode.

Important APIs, types, and functions: `struct xchk_metapath` stores scrub context, final component name, directory update structure, owned path string, parent directory inode and lock flags, transaction reservations, parent-pointer args, and scratch attr args. Public functions are `xchk_setup_metapath()`, `xchk_metapath()`, and under repair `xrep_metapath()`. Setup helpers select paths for realtime group metadata, quota directory/files, and probe requests.

Control flow: Setup rejects non-metadir filesystems and invalid generation fields, maps `sm_ino` selector values to specific metadata inodes and parent directories, installs the live child inode, and records the expected final path component. Scrub allocates an empty transaction, locks parent and child without deadlocking, looks up the name in the parent directory, and marks the child corrupt if the name is missing or points to a different inode. Repair ensures parent pointers can be stored if enabled, computes link/unlink reservations, repeatedly tries to create the correct link, removes any wrong dirent target, and handles races where the dirent changes between attempts.

State and persistence: Scrub is read-only aside from transient locks. Repair persists directory entry additions/removals and optional parent pointer updates through transactions, and can remove a bogus dirent even if the alleged child inode is missing.

Dependencies and integration points: Depends on metadir, quota, realtime group metadata inodes, directory lookup/add/remove helpers, parent pointer support, transaction reservations, inode locking, and repair transaction commit/cancel helpers. It is a final repair stage after metadata inode contents have been repaired.

Risks and test signals: Risks include deadlocks between parent/child ILOCKs, removing a valid dirent during concurrent repair, parent pointer mismatch, missing metadata inodes, and repair ordering before child metadata is stable. Test probe selector, every quota and realtime selector, missing parent directory, missing/wrong/correct dirent, bogus alleged child inode, parent-pointer present/absent cases, concurrent dirent replacement returning EAGAIN/EEXIST, and no repair on non-metadir filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/metapath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.c

Purpose: Provides common online-repair infrastructure for staging, allocating, bulk-loading, committing, or cancelling replacement btrees.

Important APIs, types, and functions: Exports initialization helpers for bare, AG-rooted, inode-fork, and metadir-inode btrees; `xrep_newbt_alloc_blocks()`, `xrep_newbt_add_extent()`, `xrep_newbt_claim_block()`, `xrep_newbt_commit()`, `xrep_newbt_cancel()`, and `xrep_newbt_unused_blocks()`. Internal helpers estimate bulk-load slack, validate allocation hints, allocate per-AG or file blocks, track reservations with autoreap, and free unused extents.

Control flow: Callers initialize `xrep_newbt` with owner info, allocation hint, reservation class, fake root storage, and bload geometry. They compute btree geometry, reserve the required number of blocks, and provide `xrep_newbt_claim_block()` to the btree bulk loader. Each claim consumes a block from the reservation list, rotates exhausted reservations, fills short or long btree pointers, and relogs deferred frees. Commit cancels autoreap for used blocks and frees unused tails through EFIs; cancel commits autoreap for all reservations so blocks are freed. Cleanup rolls deferred work periodically to avoid exceeding transaction reservation limits.

State and persistence: Tracks reserved extents in memory with perag references, used counts, and autoreap handles. Durable changes occur indirectly when callers commit staged btree roots; `newbt` ensures unused or cancelled allocations are freed or autoreaped and frees fake inode fork memory.

Dependencies and integration points: Depends on XFS allocation, deferred frees, btree staging/bulk-load, owner/rmap metadata, per-AG reservations, scrub repair transaction rolling, and inode fork caches. Used by inode btree repair and other online rebuilders.

Risks and test signals: Key risks are leaking blocks on cancellation or crash, using blocks from the wrong AG for per-AG btrees, bad slack under low space, reservation-class mistakes, and incorrect fake fork cleanup. Test ENOSPC during allocation, cancellation before any block is used, partial use with unused tail freeing, file-based vs per-AG allocation hints, custom allocation callbacks, low-free-space slack, long and short btree pointers, shutdown cleanup behavior, and EFI roll thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.h

Purpose: Defines the shared state and API for replacement-btree staging used by XFS online repair.

Important APIs, types, and functions: `struct xrep_newbt_resv` records a reserved extent, perag reference, autoreap handle, AG block start, length, and used count. `struct xrep_newbt` records scrub context, optional allocator callback, reservation list, fake btree root, owner info, bload geometry, allocation hint, and reservation type. The header declares all initialization, allocation, claim, commit/cancel, and unused-block helpers.

Control flow: Repair code initializes an `xrep_newbt`, configures its `bload` callbacks, allocates or adds extents, lets the bulk loader claim blocks, then calls commit after publishing the new root or cancel on failure.

State and persistence: The structs hold transient reservation accounting for blocks that may become durable btree blocks once a caller commits staged roots. Autoreap state is critical for crash-safe cleanup if the repair does not commit.

Dependencies and integration points: Depends on list heads, `xfs_perag`, allocation autoreap, fake btree roots, owner info, bload geometry, fsblock/agblock types, and reservation classes. It is the contract between specific repair algorithms and `newbt.c`.

Risks and test signals: Misconfigured owner info or reservation type can corrupt rmap/accounting. Test API consumers for balanced commit/cancel, correct fake-root flavor, valid allocation hints, reserved extent ownership, and no remaining unused blocks when geometry estimates are exact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.h -->
