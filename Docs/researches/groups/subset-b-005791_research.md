# subset-b-005791 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount.c

## Purpose
`refcount.c` scrubs the per-AG XFS reference count btree. It validates refcount records for shared extents and CoW staging extents, checks ordering and mergeability, cross-references refcount ownership against allocation/inode/rmap metadata, and exports helper xref checks for other scrubbers.

## Important APIs, types, and functions
The setup entry point is `xchk_setup_ag_refcountbt`, which enables intent draining when needed, runs `xrep_setup_ag_refcountbt` if repair is possible, and then uses generic AG btree setup. The main scrub entry is `xchk_refcountbt`. `struct xchk_refcnt_check` and `struct xchk_refcnt_frag` track rmap coverage while verifying a single refcount record. `struct xchk_refcbt_records` tracks previous records, shared-gap boundaries, CoW block totals, and domain ordering. Public xref helpers include `xchk_xref_is_cow_staging`, `xchk_xref_is_not_shared`, and `xchk_xref_is_not_cow_staging`.

## Control flow
`xchk_refcountbt` walks `sc->sa.refc_cur` with `xchk_btree` and `xchk_refcountbt_rec`. Each record is decoded, checked with `xfs_refcount_check_irec`, counted if CoW, checked for shared-before-CoW ordering, checked for adjacent mergeable records, and cross-referenced. Rmap verification queries overlapping rmap records, counts full-span owners immediately, saves partial fragments, and then simulates fragment coverage to prove every block reaches the advertised refcount. Shared-record gaps are queried against rmapbt to detect unrecorded overlap. After the walk, tail gaps and refcountbt/CoW block counts are checked against rmap ownership totals.

## State and persistence
The file does not persist new state. It consumes on-disk refcount/rmap/allocation/inode btrees through scrub cursors and records corruption, xref corruption, or preen bits in `sc->sm->sm_flags`. Temporary rmap fragments are heap allocated and freed during each record check.

## Dependencies and integration points
It depends on libxfs refcount and rmap btree APIs, scrub btree walkers, AG scrub setup, and repair setup from `repair.h`. Other scrubbers call its xref helpers to reject shared or CoW-staging blocks where inappropriate.

## Risks and test signals
Risk centers on fragment accounting, domain ordering, CoW single-owner semantics, and distinguishing xref failures from refcountbt corruption. Tests should cover fragmented shared extents, adjacent mergeable records, shared gaps, CoW records with non-CoW rmaps, missing rmap owners, rmapbt count mismatches, no-rmap/reflink-disabled configurations, and termination during fragment allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount_repair.c

## Purpose
`refcount_repair.c` rebuilds an AG refcount btree from rmapbt records. It derives shared extent records by sweeping overlapping file data rmaps, preserves CoW staging extents, stages a replacement refcountbt, commits it into the AGF, and reaps the obsolete tree blocks.

## Important APIs, types, and functions
`xrep_setup_ag_refcountbt` allocates an xfile-backed workspace. `struct xrep_refc` owns the xfarray of new `xfs_refcount_irec` records, a `xrep_newbt`, an `xagb_bitmap` of old refcountbt blocks, counters, and cursor position for bulk loading. Key helpers are `xrep_refc_walk_rmaps`, `xrep_refc_find_refcounts`, `xrep_refc_stash`, `xrep_refc_sort_records`, `xrep_refc_build_new_tree`, `xrep_refc_reset_counters`, `xrep_refc_remove_old_tree`, and the exported `xrep_refcountbt`.

## Control flow
Repair requires rmapbt support. It creates storage sized for one refcount record per AG block, initializes the old-tree bitmap, and scans rmaps. Shareable written data fork rmaps are fed into an `rcbag` sweep-line algorithm that emits refcount records whenever overlap depth changes above one. CoW owner records are stashed as CoW refcount records with count one, and old refcountbt owner records are remembered for later reaping. Records are sorted in on-disk domain/start order, geometry is computed with a staged fake root, blocks are reserved, `xfs_btree_bload` bulk-loads records, and `xfs_refcountbt_commit_staged_btree` installs the root.

## State and persistence
Persistent changes are the new refcountbt root and AGF counters. The code temporarily sets `pagf_repair_refcount_level` so verifiers tolerate old and new heights during AIL checkpoint/reap races, then clears it after old blocks are reaped and requests per-AG reservation reset.

## Dependencies and integration points
It depends on rmapbt as the source of truth, `xfarray`, `rcbag`, `xrep_newbt`, AG reservation accounting, staged btree bulk load, and `xrep_reap_agblocks`. The scrub setup in `refcount.c` calls its setup path before AG btree setup.

## Risks and test signals
Important risks are incorrect shareability filtering, overlap sweep off-by-one errors, refcount clamping, stale old-tree block reaping, verifier races when tree height shrinks, and insufficient AG reservation. Tests should rebuild from fragmented rmap sets, CoW staging extents, maximal refcounts, sorted shared/CoW domains, full and empty refcount trees, allocation pressure, forced termination before commit, and post-repair scrub revalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.c

## Purpose
`repair.c` provides shared infrastructure for XFS online repair. It owns repair attempt/retry semantics, transaction rolling while retaining metadata locks, block reservation estimates, AG and rtgroup cursor setup, btree root discovery, quota fallback handling, metadata inode fork repair orchestration, and reservation reset helpers.

## Important APIs, types, and functions
Core entry points include `xrep_attempt`, `xrep_will_attempt`, `xrep_failure`, `xrep_roll_ag_trans`, `xrep_roll_trans`, `xrep_defer_finish`, `xrep_ag_has_space`, `xrep_calc_ag_resblks`, `xrep_calc_rtgroup_resblks`, `xrep_fix_freelist`, `xrep_find_ag_btree_roots`, `xrep_ag_btcur_init`, `xrep_ag_init`, `xrep_rtgroup_init`, `xrep_rtgroup_btcur_init`, `xrep_require_rtext_inuse`, `xrep_reset_perag_resv`, `xrep_metadata_inode_forks`, `xrep_setup_xfbtree`, `xrep_buf_verify_struct`, `xrep_check_ino_btree_mapping`, `xrep_inode_set_nblocks`, and `xrep_reset_metafile_resv`.

## Control flow
`xrep_attempt` drops scrub cursors, calls the operation-specific repair function, records stats, and converts success, drain requests, and lock escalation into `-EAGAIN` rescrub cycles. Transaction helpers dirty and hold AG headers across rolls and deferred work completion so repairs retain exclusive metadata control. Reservation estimators read AGI/AGF when possible and fall back to worst-case btree sizes. Root finding scans rmap-owned blocks, filters AGFL blocks, validates candidate buffers by magic/uuid/verifier, and records unique highest-level roots. Metadata inode repair runs subordinate scrub/repair passes over inode, data fork, and optional attr fork.

## State and persistence
Most state is transactional or in-core: scrub flags, repair stats, AG header buffers, perag/rtgroup cursor sets, quota flags, inode extent-count flags, and metadata reservation counters. Persistent changes happen only through callers' transactions, including quota flag updates, inode core updates, superblock logging, and repaired metadata roots.

## Dependencies and integration points
This file is the common layer for all repairers declared in `repair.h`. It integrates allocation, ialloc, rmap/refcount btrees, rtgroup metadata, quota, deferred operations, scrub subordinate contexts, xfiles, buffer verifiers, and health/reservation systems.

## Risks and test signals
Risks include retry loops with unchanged corruption flags, lock retention across transaction rolls, incorrect worst-case reservations, false root detection from stale AGFL buffers, quota flag races, and rtgroup/free-space validation mistakes. Tests should cover no-repair builds, force rebuild, drain/deadlock retry paths, repair success rescrub, AGF/AGI reread identity, root discovery ambiguity, metadata inode fork cleanup, zoned realtime checks, and ENOSPC reservation reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.h

## Purpose
`repair.h` is the internal interface for XFS online repair. It declares shared repair helpers, setup functions, repair entry points, revalidators, and no-repair stubs so scrub code can compile uniformly with or without `CONFIG_XFS_ONLINE_REPAIR`.

## Important APIs, types, and functions
The header defines `xrep_notsupported`, `xrep_trans_commit`, and `struct xrep_find_ag_btree`. It declares the generic repair control helpers, AG/rtgroup setup helpers, quota helpers, xfile setup, metadata inode helpers, per-AG and realtime repair entry points, and reinitialization helpers. Under realtime and quota Kconfig blocks it either exposes real functions or maps them to `xrep_notsupported`/no-op stubs.

## Control flow
Consumers include `repair.h` and call setup/repair routines through scrub operation tables. In online-repair builds, declarations bind to concrete implementations across scrub repair files. In no-repair builds, `xrep_will_attempt` still returns true for force rebuild or corruption so `xrep_attempt` can report `-EOPNOTSUPP`; setup functions become no-ops to avoid blocking scrub-only operation.

## State and persistence
The header stores no state, but it defines the contracts for stateful repair: transaction ownership, perag/rtgroup cursors, temporary xfile buffers, quota flag updates, inode block counters, reservation resets, and staged btree roots.

## Dependencies and integration points
It depends on scrub core declarations, quota type definitions, AG reservation types, btree buffer ops, and realtime Kconfig. It is the integration point between generic scrub setup files and specialized repair modules such as rmap, refcount, rtbitmap, rtsummary, rtrmap, and rtrefcount repair.

## Risks and test signals
Risks are signature drift between declarations and implementations, incorrect stubs hiding unsupported repairs, Kconfig mismatches for realtime/quota entry points, and callers assuming setup side effects in no-repair builds. Test signals include compile coverage for repair enabled/disabled, realtime enabled/disabled, quota enabled/disabled, force rebuild on no-repair kernels, and operation tables resolving every declared repair entry correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rgb_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rgb_bitmap.h

## Purpose
`rgb_bitmap.h` provides a type-specific bitmap wrapper for realtime group block numbers (`xfs_rgblock_t`). It lets scrub and repair code manipulate ranges in rtgroup-local block units without passing raw integer types directly to the generic 32-bit bitmap API.

## Important APIs, types, and functions
The file defines `struct xrgb_bitmap`, which embeds `struct xbitmap32 rgbitmap`. Inline helpers are `xrgb_bitmap_init`, `xrgb_bitmap_destroy`, `xrgb_bitmap_set`, and `xrgb_bitmap_walk`.

## Control flow
There is no complex control flow. Callers initialize the wrapper, set ranges by `xfs_rgblock_t start` plus `xfs_extlen_t len`, walk set regions with an `xbitmap32_walk_fn`, and destroy the underlying bitmap. The wrapper forwards directly to `xbitmap32` functions.

## State and persistence
State is entirely in memory inside the embedded `xbitmap32`. Nothing is persisted, logged, or tied to a transaction by the wrapper itself.

## Dependencies and integration points
It depends on the scrub bitmap infrastructure and XFS realtime group block typedefs. It is used by realtime repair code, especially rtrmap repair and rtbitmap/rtrmap cross-reference helpers, to represent rtgroup block ranges such as CoW staging gaps or free realtime extents.

## Risks and test signals
The main risk is unit confusion: callers must supply rtgroup block numbers, not rtblocks, fsblocks, or rt extents. Range overflow and missing destroy calls are inherited from the generic bitmap. Tests should exercise large rtgroups, zero-length avoidance by callers, region coalescing, walk callback ordering, and conversions between rtb/rgbno/rtx units at call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rgb_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rgsuper.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rgsuper.c

## Purpose
`rgsuper.c` scrubs and repairs the realtime group superblock metadata. In the current implementation only rtgroup 0 has a superblock, so scrub mainly obtains the rtgroup, locks the realtime bitmap enough to stabilize the group, and cross-references the superblock block against realtime allocation/rmap metadata.

## Important APIs, types, and functions
The setup function is `xchk_setup_rgsuperblock`, which allocates a zero-block transaction. `xchk_rgsuperblock` performs the scrub. `xchk_rgsuperblock_xref` checks that realtime block zero is allocated and owned by filesystem metadata. With online repair enabled, `xrep_rgsuperblock` logs the superblock.

## Control flow
Scrub rejects any rtgroup number other than zero with `-ENOENT`. It obtains an existing rtgroup reference with `xchk_rtgroup_init_existing`, locks the bitmap in shared mode with `XFS_RTGLOCK_BITMAP_SHARED`, and relies on mount-time structural validation of the realtime superblock. It then runs cross-reference checks against rtbitmap and rtrmap. Repair asserts group zero and calls `xfs_log_sb` in the active transaction.

## State and persistence
Scrub records only corruption/xref flags in the scrub metadata. Repair persists by logging the filesystem superblock, not by reconstructing an independent per-group structure.

## Dependencies and integration points
It depends on rtgroup lookup/locking, realtime bitmap xref helper `xchk_xref_is_used_rt_space`, rtrmap helper `xchk_xref_is_only_rt_owned_by`, and generic scrub transaction setup. It integrates with realtime group scrub types and the repair dispatch table.

## Risks and test signals
Risks include future rtgroup formats where nonzero groups gain superblock-like data, races with group teardown, and xref behavior when rtrmap or rtbitmap cursors are unavailable. Tests should cover group zero, nonzero `-ENOENT`, missing rtgroup, shared bitmap locking, rmap owner mismatch for block zero, free block zero, and repair logging under online repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rgsuper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap.c

## Purpose
`rmap.c` scrubs the per-AG reverse mapping btree. It validates rmap records, detects illegal overlaps and mergeable adjacent records, cross-references mapped space with allocation, inode, and refcount metadata, and compares AG metadata rmaps against independently collected metadata block bitmaps.

## Important APIs, types, and functions
`xchk_setup_ag_rmapbt` prepares AG rmap scrub and optional repair. `struct xchk_rmap` tracks previous/overlap records and bitmaps for `OWN_FS`, `OWN_LOG`, `OWN_AG`, `OWN_INOBT`, and `OWN_REFC`. Important helpers are `xchk_rmapbt_xref_refc`, `xchk_rmapbt_check_unwritten_in_keyflags`, `xchk_rmapbt_check_overlapping`, `xchk_rmapbt_check_mergeable`, `xchk_rmapbt_walk_ag_metadata`, `xchk_rmapbt_mark_bitmap`, `xchk_rmapbt_check_bitmaps`, and `xchk_rmapbt`. Exported xref helpers include `xchk_xref_is_only_owned_by`, `xchk_xref_is_not_owned_by`, and `xchk_xref_has_no_owner`.

## Control flow
Scrub builds expected AG metadata bitmaps by walking AG headers, log placement, bnobt/cntbt/rmapbt/AGFL, inode btrees, finobt, and refcountbt. It then walks the rmapbt. Each record is decoded and checked, btree node key flags are inspected for stale unwritten bits, mergeability and overlap rules are applied, cross-reference checks are run, and matching metadata bitmap ranges are cleared. After the walk, remaining set bits indicate missing rmap coverage.

## State and persistence
The file is read-only from a filesystem perspective. It records scrub flags and uses temporary `xagb_bitmap` state. Preen is used for historical unwritten bits in internal rmap keys; corrupt and xcorrupt flags distinguish primary failures from cross-reference mismatches.

## Dependencies and integration points
It depends on allocation, inode, refcount, rmap btree APIs, AGFL walking, scrub bitmap helpers, and repair setup. Many other scrubbers rely on its xref helpers to validate ownership constraints.

## Risks and test signals
Risks include false xref corruption from incomplete metadata bitmap walks, shareability filtering mistakes for reflink data, stale key flag handling, AGFL stale block confusion, and owner/unit mismatches. Tests should cover overlapping metadata rmaps, overlapping shared data, adjacent mergeable records, internal log AGs, sparse inode btrees, finobt/refcountbt optional features, stale unwritten key flags, and missing or extra AG metadata rmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap_repair.c

## Purpose
`rmap_repair.c` rebuilds a per-AG rmapbt by deriving reverse mappings from primary metadata and file forks. It is the most complex AG btree repair because it must scan inodes while tracking live rmap updates, reserve space for the new rmapbt without recursive rmap changes, bulk-load the replacement tree, and reap the old tree blocks.

## Important APIs, types, and functions
`xrep_setup_ag_rmapbt` enables rmap filesystem gates, creates xfile storage, and allocates `struct xrep_rmap`. That context owns a `xrep_newbt`, mutex, in-memory `xfbtree`, rmap hook, inode scan cursor, record counts, and old AGF counters. Major helpers include `xrep_rmap_stash`, inode fork scanners, `xrep_rmap_find_inode_rmaps`, `xrep_rmap_find_refcount_rmaps`, `xrep_rmap_find_rmaps`, `xrep_rmap_reserve_space`, `xrep_rmap_build_new_tree`, `xrep_rmap_remove_old_tree`, live update hook `xrep_rmapbt_live_update`, and exported `xrep_rmapbt`.

## Control flow
The repair first records non-space metadata rmaps under AG locks, then drops AG buffers and uses an empty transaction while scanning every inode fork for mappings into the target AG. A live rmap hook updates the in-memory btree for already-scanned owners. After relocking the AG, collected records are validated and counted. Space reservation iteratively allocates new rmapbt blocks in no-rmap mode, recomputes `OWN_AG` records for bnobt/cntbt/AGFL/new rmapbt blocks, and repeats until geometry is stable. The new tree is bulk-loaded and committed to AGF, counters are reset, and old rmapbt blocks are inferred from gaps not present in bnobt free space.

## State and persistence
Persistent state includes the new rmapbt root and AGF `btreeblks`/rmap counters. Temporary state includes xfile-backed in-memory btree, inode scan cursor, live update hook, and reservation lists. `pagf_repair_rmap_level` tolerates tree height transitions until old blocks are reaped and reservations reset.

## Dependencies and integration points
It integrates inode scanning, bmap btree walking, inode btree/refcount metadata derivation, AG allocation, rmap hooks, staged btree bulk loading, and reaping. It also understands metadir realtime btree inodes because their blocks live on the data device and must have AG rmaps.

## Risks and test signals
Risks include stale in-memory records if live hooks miss updates, deadlocks during inode scan, recursive allocation/rmap updates, old-tree block misidentification, and incorrect bmbt/realtime fork filtering. Tests should cover concurrent file changes, attr/data forks, btree and extent forks, reflink CoW, empty inobt root, internal log, AGFL churn, low free space, hook failure aborts, and post-repair rmap/refcount scrub consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtb_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtb_bitmap.h

## Purpose
`rtb_bitmap.h` provides a type-specific bitmap wrapper for filesystem-wide realtime block numbers (`xfs_rtblock_t`). It gives scrub and repair code a small strongly named abstraction over the generic 64-bit bitmap implementation.

## Important APIs, types, and functions
The file defines `struct xrtb_bitmap`, embedding `struct xbitmap64 rtbitmap`. Inline functions are `xrtb_bitmap_init`, `xrtb_bitmap_destroy`, `xrtb_bitmap_set`, and `xrtb_bitmap_walk`.

## Control flow
Callers initialize the bitmap, add ranges in rtblock units, walk all set ranges with an `xbitmap64_walk_fn`, and destroy the wrapper. All operations forward directly to the underlying `xbitmap64`.

## State and persistence
The wrapper owns only transient in-memory bitmap state. It performs no logging, allocation policy, or disk updates by itself.

## Dependencies and integration points
It depends on XFS realtime block typedefs and scrub bitmap infrastructure. It is suitable for code that needs whole-realtime-volume addressing rather than rtgroup-local `xrgb_bitmap` or data-device `xfsb_bitmap`.

## Risks and test signals
The main risk is unit mismatch at call sites, particularly confusing rtblocks with rt extents, rtgroup blocks, or fsblocks. Tests should check high rtblock values requiring 64-bit coverage, range coalescing, walk ordering, destroy paths, and conversions at callers that cross group boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtb_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.c

## Purpose
`rtbitmap.c` scrubs the realtime bitmap metadata for an rtgroup. It verifies realtime geometry fields, metadata inode shape, mapped/written bitmap file extents, free extent records returned by rt allocation queries, and cross-references free/used realtime space against rtrmap and rtrefcount metadata.

## Important APIs, types, and functions
`xchk_setup_rtbitmap` allocates `struct xchk_rtbitmap`, initializes the rtgroup, optional repair setup, transaction reservation, live bitmap inode, dquots, and rtgroup locks. `xchk_rtbitmap` is the main scrubber. Helpers include `xchk_rtbitmap_xref`, `xchk_rtbitmap_rec`, `xchk_rtbitmap_check_extents`, and exported `xchk_xref_is_used_rt_space`.

## Control flow
Setup computes expected `rextents`, `rextslog`, and `rbmblocks` after locking the rtgroup to avoid growfs races. Scrub compares superblock geometry against computed values, checks bitmap file size/alignment, delegates inode/fork scrutiny to metadata inode scrub, and ensures the file has only written mappings. It then walks all free realtime extents with `xfs_rtalloc_query_all`. Each record is verified, cross-referenced as having no rtrmap owner and no shared/CoW refcount records, and gaps between free records are checked as owned. The tail of the group is checked similarly.

## State and persistence
Scrub is read-only and updates only scrub flags plus `next_free_rgbno` in the transient `xchk_rtbitmap`. No bitmap changes are written here; repair lives in `rtbitmap_repair.c`.

## Dependencies and integration points
It depends on rtgroup locking, rt allocation query APIs, metadata inode fork scrub, bmap read APIs, rtrmap xref helpers, rtrefcount helpers, zone validation for zoned filesystems, and repair setup through `rtbitmap.h`.

## Risks and test signals
Risks include off-by-one tail checks, extent/rtblock/rtgroup-block conversion mistakes, growfs races, zoned filesystem special cases, and inability to xref when rtrmap is unavailable. Tests should cover zero-sized rt volumes, oversized `rbmblocks`, unwritten or hole bitmap mappings, malformed free extents, free extents with rmap owners, used gaps without owners, rtreflink CoW/shared conflicts, and zoned rtgroup bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.h

## Purpose
`rtbitmap.h` defines the shared scrub/repair state for realtime bitmap checks and repairs. It also defines word-offset types for xfile-backed bitmap reconstruction and the buffer sizing helper used by setup.

## Important APIs, types, and functions
It defines `xrep_wordoff_t`, `xrep_wordcnt_t`, `XREP_RTBMP_WORDMASK`, and `struct xchk_rtbitmap`. The state structure stores scrub context, computed geometry (`rextents`, `rbmblocks`, `rextslog`), block reservation, scan cursors (`next_free_rgbno`, `next_rgbno`), rtgroup lock flags, xfile write position, optional repair `xfs_rtalloc_args` and `xrep_tempexch`, and flexible `words[]` storage. It declares `xrep_setup_rtbitmap` or a stub and defines `xchk_rtbitmap_wordcnt`.

## Control flow
`xchk_setup_rtbitmap` allocates this structure with a flexible array sized by `xchk_rtbitmap_wordcnt`. Scrub uses the geometry and `next_free_rgbno`; repair uses the xfile word buffer, copy position, temporary exchange state, and rt allocation arguments.

## State and persistence
The header defines transient state only. Persistent bitmap repairs occur through the implementation in `rtbitmap_repair.c`, which uses this structure to stage and exchange file contents.

## Dependencies and integration points
It depends on realtime bitmap word sizing, scrub context types, online repair Kconfig, and `xrep_tempexch`. It is included by both realtime bitmap scrub and repair code to keep their shared layout consistent.

## Risks and test signals
Risks include allocating an undersized `words[]` buffer, mismatching xfile word offsets with on-disk bitmap headers, and stale fields when setup exits early. Tests should cover repair and no-repair builds, block-size-dependent word counts, large bitmap files, rtgroup-enabled versus legacy raw word formats, and setup error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap_repair.c

## Purpose
`rtbitmap_repair.c` reconstructs the realtime bitmap file for an rtgroup. It builds a new bitmap in an xfile from gaps in the realtime rmapbt, fixes bitmap geometry and inode mapping problems, copies the reconstructed blocks into a temporary file, atomically exchanges contents with the real bitmap file, and reaps old mappings.

## Important APIs, types, and functions
`xrep_setup_rtbitmap` creates a tempfile, xfile, and reservation estimate. Word helpers include `xfbmp_load`, `xfbmp_store`, `xfbmp_copyin`, and `xfbmp_copyout`. Rebuild helpers are `xrep_rtbitmap_mark_free`, `xrep_rtbitmap_walk_rtrmap`, `xrep_rtbitmap_find_freespace`, `xrep_rtbitmap_prep_buf`, `xrep_rtbitmap_data_mappings`, `xrep_rtbitmap_geometry`, and exported `xrep_rtbitmap`.

## Control flow
Repair requires rtrmapbt and exchange-range support. It repairs metadata inode forks, joins the bitmap inode, converts unwritten mappings when possible, fixes superblock geometry and file size, flushes busy extents, then reconstructs free bits by walking rtrmap records and marking gaps as free. Free regions must be rt extent aligned and must not overlap rtrefcount shared or CoW records. The xfile bitmap is copied into a preallocated tempfile with proper rtbitmap buffer headers, the tempfile size is set, `xrep_tempexch_contents` swaps data fork contents, and the old bitmap blocks are reaped from the temp inode.

## State and persistence
Persistent updates include superblock realtime geometry counters, bitmap inode size/fork contents, converted written extents, and exchanged bitmap data. Temporary state includes xfile words, tempfile inode, `xrep_tempexch`, `prep_wordoff`, and rtrmap walk cursor `next_rgbno`.

## Dependencies and integration points
It depends on rtrmap as the truth source for used realtime blocks, rtrefcount for shared/CoW exclusion, tempfile/tempexch repair helpers, bmap conversion, extent busy flushing, rtbitmap buffer verifiers, and metadata inode repair.

## Risks and test signals
Risks include deriving free space from corrupt rtrmap data, alignment errors at word/rt extent boundaries, reservation underestimation before dirty transactions, exchange-range failure after staging, and mishandling legacy versus rtgroup bitmap headers. Tests should cover fragmented free gaps, word-boundary gaps, final tail free space, shared/CoW conflicts, unwritten bitmap extents, large bitmap files, busy extents, no exchange-range support, and post-repair bitmap/summary/rtrmap scrub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount.c

## Purpose
`rtrefcount.c` scrubs the realtime refcount btree for an rtgroup. It mirrors AG refcount scrub logic but uses rtgroup-local block units, checks realtime extent alignment, validates the metadata inode, and cross-references records against realtime bitmap, realtime rmap, and data-device rmaps for the rtrefcount btree inode.

## Important APIs, types, and functions
`xchk_setup_rtrefcountbt` initializes rtgroup state, optional repair setup, live rtrefcount inode, and all rtgroup locks. `xchk_rtrefcountbt` is the main scrubber. `struct xchk_rtrefcnt_check` and `xchk_rtrefcnt_frag` implement rmap fragment counting. `struct xchk_rtrefcbt_records` tracks previous records, unshared gaps, CoW block totals, and domain order. Xref helpers are `xchk_xref_is_rt_cow_staging`, `xchk_xref_is_not_rt_shared`, and `xchk_xref_is_not_rt_cow_staging`.

## Control flow
After metadata inode fork scrub, `xchk_btree` walks `sc->sr.refc_cur`. Each record is decoded, checked with `xfs_rtrefcount_check_irec`, verified to start and end on realtime extent boundaries, checked for shared-before-CoW ordering and mergeability, and cross-referenced. Rmap xref counts complete and fragmentary rtrmap records to prove the advertised refcount. Shared-record gaps are queried for unexpected overlaps. Final checks compare rtrefcount btree block counts against data-device rmap ownership for the metadata inode and CoW blocks against realtime rmap ownership.

## State and persistence
The file is read-only and sets scrub flags. Temporary fragment lists are allocated per record. It uses `sc->sr` realtime cursors and `sc->sa.rmap_cur` when counting data-device blocks belonging to the rtrefcount metadata btree inode.

## Dependencies and integration points
It depends on rtgroup locking, rtrefcount/rtrmap btree APIs, realtime bitmap xref, metadata inode fork scrub, and repair setup. Realtime rmap and bitmap scrubbers call its xref helpers to reject shared or CoW-staging ranges.

## Risks and test signals
Risks include unit conversion errors, full-rt-extent alignment checks, fragment coverage mistakes, and mismatched data-device rmap counts for metadir btree blocks. Tests should cover aligned and misaligned records, fragmented shared realtime extents, CoW records, shared gaps, missing rtrmap owners, wrong metadata inode rmaps, no-rtreflink paths, and xref skip/failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount_repair.c

## Purpose
`rtrefcount_repair.c` rebuilds an rtgroup realtime refcount btree from realtime rmap records. It derives shared extents by sweeping rtrmap overlap depth, preserves CoW staging extents, stages a new metadata-inode btree, commits it to the rtrefcount inode, and reaps old btree blocks from the data device.

## Important APIs, types, and functions
`xrep_setup_rtrefcountbt` allocates xfile workspace. `struct xrep_rtrefc` owns the new refcount record xfarray, `xrep_newbt`, old-block `xfsb_bitmap`, scrub pointer, load cursor, and block count. Key helpers include `xrep_rtrefc_check_ext`, `xrep_rtrefc_stash`, `xrep_rtrefc_walk_rmaps`, `xrep_rtrefc_find_refcounts`, `xrep_rtrefc_scan_ag`, `xrep_rtrefc_sort_records`, `xrep_rtrefc_build_new_tree`, and exported `xrep_rtrefcountbt`.

## Control flow
Repair requires rtrmapbt support and first repairs metadata inode forks. It scans every data AG rmapbt to find old blocks owned by the rtrefcount inode data fork. It then initializes rtgroup btree cursors and sweeps the realtime rmapbt with an `rcbag`. Shareable written realtime file mappings produce shared refcount records when overlap depth changes above one; CoW owner records are preserved as CoW domain records. Records are sorted by encoded start/domain, geometry is computed for an inode-rooted staged btree, extra transaction reservation is taken against the rtrefcount inode, blocks are allocated, the tree is bulk-loaded, and the staged btree is committed.

## State and persistence
Persistent updates include the rtrefcount inode data fork, inode block count/quota accounting, and new metadata btree contents. Old btree blocks are tracked as fsblocks and reaped with `xrep_reap_metadir_fsblocks`. Temporary xfarray, rcbag, staged fake inode root, and xfile storage are destroyed on exit.

## Dependencies and integration points
It depends on rtrmap as the truth source, data-device rmapbt for locating metadir btree blocks, `xrep_newbt` metadir inode support, `rcbag`, metadata inode repair, and realtime in-use validation via `xrep_require_rtext_inuse`.

## Risks and test signals
Risks include deriving counts from corrupt rtrmap, allowing metadata or unwritten rmaps into shared calculations, missing old data-device btree blocks, transaction reservation underestimation, and root-format mistakes for metadir btrees. Tests should cover fragmented overlaps, CoW staging, misaligned realtime extents, no rtrmapbt support, large rtextent counts, old btree reaping, quota/block-count updates, and post-repair scrub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap.c

## Purpose
`rtrmap.c` scrubs the realtime reverse mapping btree for an rtgroup. It validates rtrmap records, checks illegal overlaps and mergeable adjacent records, verifies the rtrmap metadata inode, and cross-references realtime ownership against rtbitmap and rtrefcount metadata.

## Important APIs, types, and functions
`xchk_setup_rtrmapbt` prepares rtgroup state, optional repair, live rtrmap inode, and rtgroup locks. `struct xchk_rtrmap` tracks the furthest overlapping record and previous record. Main helpers are `xchk_rtrmapbt_check_overlapping`, `xchk_rtrmap_mergeable`, `xchk_rtrmapbt_check_mergeable`, `xchk_rtrmapbt_xref_rtrefc`, `xchk_rtrmapbt_xref`, `xchk_rtrmapbt_rec`, and `xchk_rtrmapbt`. Exported xref helpers are `xchk_xref_has_no_rt_owner`, `xchk_xref_has_rt_owner`, and `xchk_xref_is_only_rt_owned_by`.

## Control flow
After setup and metadata inode fork scrub, `xchk_btree` walks `sc->sr.rmap_cur`. Each record is decoded and checked with `xfs_rtrmap_check_irec`. If still clean, it checks whether adjacent records should have merged, whether overlaps are legal shareable realtime data mappings, and whether the range is used in the rtbitmap. CoW records are checked against CoW staging metadata, and non-CoW records are checked against rtrefcount to ensure shared extents describe valid written data owners.

## State and persistence
Scrub is read-only and records flags in scrub metadata. The local `xchk_rtrmap` context stores only previous/overlap records for one btree walk.

## Dependencies and integration points
It depends on rtgroup locks, rtrmap btree APIs, metadata inode fork scrub, rtbitmap used-space xref, rtrefcount xref, and repair setup. Other realtime scrubbers use its exported xref helpers to prove presence or absence of realtime owners.

## Risks and test signals
Risks include permissive overlap checks, incorrect shareability when rtreflink is disabled, use of AG refcount helper names in CoW xref paths, and owner-count false positives. Tests should include overlapping metadata records, overlapping shared realtime file records, unwritten shared extents, adjacent mergeable records, free-space rmaps, shared extents without rtrefcount records, CoW staging mismatches, and missing metadata inode blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap_repair.c

## Purpose
`rtrmap_repair.c` rebuilds an rtgroup realtime rmap btree. It scans realtime file data mappings and CoW staging extents into an in-memory btree, tracks live rtrmap updates during the inode scan, finds old rtrmapbt blocks through data-device rmaps, bulk-loads a new metadir btree into the realtime rmap inode, and reaps obsolete blocks.

## Important APIs, types, and functions
`xrep_setup_rtrmapbt` enables rmap gates, creates xfile storage, and stores `struct xrep_rtrmap` in `sc->buf`. That context owns `xrep_newbt`, a mutex, in-memory `xfbtree`, old-block `xfsb_bitmap`, live rmap hook, inode scan cursor, memory cursor, and record count. Major helpers are `xrep_rtrmap_stash`, `xrep_rtrmap_scan_dfork`, `xrep_rtrmap_scan_inode`, `xrep_rtrmap_find_refcount_rmaps`, `xrep_rtrmap_find_rmaps`, `xrep_rtrmap_build_new_tree`, `xrep_rtrmapbt_live_update`, setup/teardown helpers, and exported `xrep_rtrmapbt`.

## Control flow
Repair first fixes metadata inode forks. Scan setup initializes the in-memory rtrmapbt and installs a live rmap hook for the rtgroup. It records the realtime superblock range when present, records CoW staging extents from rtrefcount, unlocks realtime metadata, and scans all inodes. Only realtime data forks are accumulated; mappings are coalesced when physically and logically adjacent. After relocking realtime metadata, it scans all AG rmapbts for old rtrmap inode blocks, validates collected records against rtbitmap in-use state, computes staged btree geometry, reserves blocks on the rtrmap inode, bulk-loads from the in-memory tree, commits the staged btree, updates inode block counts, stops live updates, commits new blocks, and reaps old metadir fsblocks.

## State and persistence
Persistent state is the rebuilt rtrmap inode data fork and inode block accounting. Temporary state includes xfile-backed in-memory btree, old-block bitmap, inode scan cursor, live update hook, staged fake root, and temporary transactions used by hooks.

## Dependencies and integration points
It depends on inode cache scanning, realtime bmap conversion helpers, rtrefcount CoW records, rtbitmap in-use validation, data-device rmapbt for metadir block discovery, `xrep_newbt` metadir inode support, and rmap update notifier hooks.

## Risks and test signals
Risks include missed live updates, incorrect realtime fork filtering, old btree block leaks, stale CoW staging records, unit conversion between rtblock and rgbno, and lock ordering during long scans. Tests should cover concurrent realtime file changes, loaded and unloaded bmbt forks, unwritten mappings, rt superblock owner record, CoW staging, no realtime files, hook aborts, metadir old-block reaping, and post-repair rtrmap/rtbitmap/rtrefcount scrub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.c

## Purpose
`rtsummary.c` scrubs the realtime summary file. It recomputes summary counters from the realtime bitmap into an xfile and compares that computed image against the on-disk rtsummary metadata inode, while also validating summary geometry and file mappings.

## Important APIs, types, and functions
`xchk_setup_rtsummary` allocates `struct xchk_rtsummary`, initializes rtgroup state, optional repair setup, xfile storage, transaction reservation, live summary inode, dquots, and rtgroup locks. Helper APIs include `xfsum_load`, `xfsum_store`, exported `xfsum_copyout`, `xchk_rtsum_inc`, `xchk_rtsum_record_free`, `xchk_rtsum_compute`, `xchk_rtsum_compare`, and main `xchk_rtsummary`.

## Control flow
Setup locks realtime bitmap/summary state and computes expected `rextents`, `rbmblocks`, `rsumblocks`, and `rsumlevels`. Scrub compares superblock/mount geometry and summary inode size/alignment, then runs metadata inode fork scrub. It computes a fresh summary by querying all free extents in the realtime bitmap; each free extent determines a bitmap block offset and length-log bucket whose counter is incremented in the xfile. Comparison first verifies all summary file extents are written, then reads each on-disk rtsummary block and compares it with the xfile-computed words.

## State and persistence
Scrub writes only to the transient xfile and scrub flags. It handles both rtgroup big-endian raw suminfo and legacy in-memory increment formats through `xchk_rtsum_inc`. Repair setup and repair implementation are separate.

## Dependencies and integration points
It depends on rtbitmap correctness, realtime allocation query APIs, xfile pageable storage, bmap read helpers, metadata inode scrub, rtgroup locks, and repair setup through `rtsummary.h`. It treats bitmap corruption as an xref corruption against the bitmap inode.

## Risks and test signals
Risks include counter overflow/mis-bucketing by `highbit`, stale geometry during growfs, byte-order mismatches, unwritten summary extents, and false blame when bitmap is corrupt. Tests should cover varied free extent sizes, empty and full realtime volumes, summary files larger than computed size, mismatched `m_rsumlevels`/`m_rsumblocks`, legacy versus rtgroup raw words, unwritten mappings, and intentionally corrupted bitmap input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.h

## Purpose
`rtsummary.h` defines the shared state and small API surface for realtime summary scrub and repair. It keeps geometry, xfile copy position, rtalloc buffer arguments, repair exchange state, and a flexible comparison buffer in one structure.

## Important APIs, types, and functions
The central type is `struct xchk_rtsummary`, with optional `xrep_tempexch`, `xfs_rtalloc_args`, computed `rextents`, `rbmblocks`, `rsumblocks`, `rsumlevels`, repair reservation `resblks`, `prep_wordoff`, and flexible `words[]`. It declares `xfsum_copyout` for reading computed xfile summary words and `xrep_setup_rtsummary` or a no-op stub.

## Control flow
`xchk_setup_rtsummary` allocates this structure with a block-sized `words[]` buffer. Scrub uses the geometry and buffer for compute/compare. Repair setup can add reservation and temporary exchange state before the common scrub setup allocates a transaction.

## State and persistence
The header defines in-memory scrub/repair state only. Persistent changes are made by implementation files that use this structure to compare or replace rtsummary contents.

## Dependencies and integration points
It depends on realtime allocation argument structures, online repair Kconfig, `xrep_tempexch`, and the xfile summary format used by `rtsummary.c` and its repair counterpart. It links scrub and repair code without exposing internal xfile helper functions broadly.

## Risks and test signals
Risks include flexible array sizing mismatches, stale geometry fields after growfs races, incorrect `prep_wordoff` use during repair copyout, and no-repair builds accidentally depending on repair state. Tests should compile repair and no-repair configurations, exercise block-size-sized buffers, large summary files, rtgroup and legacy formats, and early setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.h -->
