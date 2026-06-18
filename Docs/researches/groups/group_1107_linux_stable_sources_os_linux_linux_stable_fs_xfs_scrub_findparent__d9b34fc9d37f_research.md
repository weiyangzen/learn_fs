# Group Research: group_1107_linux_stable_sources_os_linux_linux_stable_fs_xfs_scrub_findparent__d9b34fc9d37f

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.c

This file implements the online repair helper for finding the parent directory of a directory inode. It supports brute-force filesystem directory scans, live directory-update hooks, special-case self references, and a dcache shortcut.

Key structures and state:
- `struct xrep_findparent_info` tracks the directory currently being scanned, the scrub context, optional scan state, the discovered parent inode, and whether that parent was only tentatively observed.
- It depends on the live inode scanner from `iscan.c`, directory walkers, dirent hooks, tempfile filtering, and XFS inode health flags.

Main control flow:
- `__xrep_findparent_scan_start` validates that dirent fsgates are enabled, initializes `xchk_iscan`, registers a directory hook, and initializes `parent_ino` under a mutex.
- `xrep_findparent_scan` iterates every allocated inode with `xchk_iscan_iter`, filters to directories, scans each directory for a child entry pointing at `sc->ip`, marks visited inodes, and releases references.
- `xrep_findparent_dirent` ignores invalid, dot, and dotdot names, records a single valid parent, rejects multiple parents as corruption, and updates `xrep_parent_scan_info` if present.
- `xrep_findparent_live_update` applies dirent add/remove notifications for directories already visited by the live scan, keeping the scan result coherent with concurrent changes.
- `xrep_findparent_confirm` verifies a proposed parent by special-casing root/metadir root/unlinked directories, validating the parent inode number, loading it, checking it is a directory, and scanning it.
- `xrep_findparent_self_reference` returns known self-parent values for root directories and root fallback for unlinked directories.
- `xrep_findparent_from_dcache` tries `d_find_alias` and `dget_parent` as a fast parent hint.

Important invariants:
- The target directory’s ILOCK is not held during full filesystem scans; callers must retake it before reading results.
- Scanned directories are skipped if they are the target, a repair tempfile, in the wrong metadata tree, sick in core/bmbtd/dir, or zapped.
- Multiple parent dirents for one directory are treated as corruption.
- Live updates are selected only for already visited inode ranges via `xchk_iscan_want_live_update`.

Risks and edge cases:
- Corrupt directory entries, sick directories, or zapped directories abort or defer repair rather than producing unreliable parent results.
- Dcache lookup is only a hint and is not a consistency proof.
- The scan relies on dirent fsgates and hooks to avoid missing concurrent parent changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.h

This header declares the parent-finding scan interface used by XFS online repair.

Key definitions:
- `struct xrep_parent_scan_info` holds the scrub context, live inode scan cursor, directory update hook, mutex-protected `parent_ino`, and a `lookup_parent` flag.
- `xrep_findparent_scan_start` is the default wrapper around `__xrep_findparent_scan_start` with the built-in live update hook.
- `xrep_findparent_scan_found` stores a discovered parent under `pscan->lock`.

Exported operations:
- Start, run, finish early, and tear down a parent scan.
- Confirm a candidate parent inode.
- Detect self-reference cases.
- Query the dcache for a parent hint.

Integration notes:
- Includes `struct xchk_iscan` and `struct xfs_dir_hook`, tying this header directly to live inode scanning and directory-update notifications.
- The mutex exists because scan code and hook callbacks can update `parent_ino` concurrently.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fsb_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fsb_bitmap.h

This header provides a type-specific wrapper around `xbitmap64` for filesystem block numbers.

Key definition:
- `struct xfsb_bitmap` contains an `xbitmap64 fsbitmap`.

Provided helpers:
- `xfsb_bitmap_init`
- `xfsb_bitmap_destroy`
- `xfsb_bitmap_set`
- `xfsb_bitmap_walk`

Purpose and integration:
- The wrapper makes bitmap use type-aware for `xfs_fsblock_t` ranges and `xfs_filblks_t` lengths.
- It delegates all storage and walking behavior to the generic 64-bit bitmap implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fsb_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.c

This file scrubs XFS filesystem summary counters: inode count, free inode count, free data blocks, and free realtime extents. It computes expected values from incore AG and realtime metadata, compares them with percpu/global counters, and decides whether discrepancies are corruption or live-race noise.

Key state:
- Uses `struct xchk_fscounters` from `fscounters.h`.
- `XCHK_FSCOUNT_MIN_VARIANCE` provides minimum tolerance for unfrozen live scans.

Setup and freeze behavior:
- `xchk_setup_fscounters` allocates state, records valid inode count bounds, warms per-AG AGI/AGF state, optionally freezes the filesystem for repair or try-harder scans, and allocates an empty transaction.
- `xchk_fscount_warmup` reads AGI/AGF headers for any uninitialized per-AG state.
- `xchk_fscounters_freeze` drops write protection if held, repeatedly tries a kernel freeze, and marks the state frozen.
- `xchk_fscounters_cleanup` thaws on cleanup and logs emergency if thaw fails.

Counting behavior:
- `xchk_fscount_aggregate_agcounts` sums per-AG inode/free inode/free block values, includes freelist and btree blocks, subtracts per-AG and global reservations, subtracts delayed allocation blocks, and rejects nonsensical totals.
- For non-lazy sbcount filesystems, `xchk_fscount_btreeblks` counts bno/cnt btree blocks directly.
- Realtime support counts free realtime extents by querying each rtgroup bitmap and accounts for delayed realtime allocations; zoned filesystems skip frextents checks.

Comparison behavior:
- `xchk_fscount_within_range` accepts exact matches, or for non-repair live scans accepts expected values between before/after percpu sums.
- `xchk_fscounters` snapshots counters, rejects negative or impossible values, computes expected counters, counts realtime extents, compares all counters, and returns `-EDEADLOCK` when an unfrozen live scan needs userspace to retry with stronger stabilization.

Important invariants:
- Any counting failure marks the scrub incomplete so repair will not use partial data.
- Repair requires exact counter matches and a frozen filesystem.
- Negative free counters during an unfrozen scan can be transient due to racing reservations; frozen negatives are corruption.

Risks and edge cases:
- Busy live filesystems can produce `-EDEADLOCK` rather than false corruption.
- Pre-lazysbcount filesystems require deeper btree block counting.
- Zoned filesystems intentionally avoid on-disk frextents repair semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.h

This header defines the scrub-time state for filesystem counter checking and repair.

Key structure:
- `struct xchk_fscounters`
  - `sc`: owning scrub context.
  - `icount`, `ifree`, `fdblocks`: computed expected global counters.
  - `frextents`, `frextents_delayed`: realtime free extent accounting.
  - `icount_min`, `icount_max`: valid inode count bounds from filesystem geometry.
  - `frozen`: whether scrub/repair froze the filesystem.

Integration:
- Used by `fscounters.c` for checking and by `fscounters_repair.c` for resetting counters from computed values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters_repair.c

This file repairs filesystem summary counters by resetting incore counters to values computed during scrub.

Main operation:
- `xrep_fscounters` requires `fsc->frozen` to be true, traces the reset, then sets:
  - `m_icount`
  - `m_ifree`
  - free data blocks via `xfs_set_freecounter`
  - free realtime extents where applicable.

Important behavior:
- If the filesystem was not frozen, it asserts and returns `-EFSCORRUPTED`; repair must not race live writers.
- Online repair is assumed to run on v5 filesystems with lazy superblock counters, so it does not update `sb_fdblocks`.
- `sb_frextents` is handled carefully because realtime free extent accounting differs with rtgroups and delayed realtime reservations.

Integration:
- Consumes `struct xchk_fscounters` populated by `xchk_fscounters`.
- Forces consistency between computed scrub state and the mount’s in-memory counters.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/health.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/health.c

This file maps scrub results to XFS incore health state. It centralizes how online scrub and repair set or clear sick flags on filesystem, allocation group, inode, and realtime group objects.

Key data:
- `enum xchk_health_group` classifies a scrub type as filesystem-wide, AG, inode, rtgroup, or none.
- `type_to_health_flag` maps every `XFS_SCRUB_TYPE_*` to a sick-mask group and mask.

Main operations:
- `xchk_health_mask_for_scrub_type` returns the default sick mask for a scrub type.
- `xchk_mark_healthy_if_clean` adds extra flags to `healthy_mask` when scrub found no direct or cross-reference corruption.
- `xchk_file_looks_zapped` checks whether inode metadata appears previously zapped, except during post-repair revalidation.
- `xchk_update_health` applies scrub results:
  - corrupt/xcorrup shows as sick
  - clean clears `sick_mask | healthy_mask`
  - `HEALTHY` scrub clears indirect health flags after a clean full scan
  - inode repair requests add `XFS_SICK_INO_FORGET`
- `xchk_ag_btree_del_cursor_if_sick` drops cross-reference btree cursors if their known health is bad, setting `XFAIL`.
- `xchk_health_record` checks existing primary health flags across fs, AGs, and rtgroups and marks corruption if any remain.

Important invariants:
- Runtime scrub errors do not update health; only completed scrub results do.
- Repairers that rebuild multiple structures are expected to expand the sick mask.
- Cross-reference scans avoid relying on metadata already marked sick, except when scrubbing the same structure or revalidating freshly repaired AG metadata.

Risks and edge cases:
- Health state is intentionally conservative when repair is requested, to avoid stale inode sickness propagating after inactivation.
- `XFS_SCRUB_TYPE_HEALTHY` has special behavior because it clears indirect evidence, not one direct metadata type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/health.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/health.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/health.h

This header declares scrub health integration helpers.

Exports:
- `xchk_health_mask_for_scrub_type`
- `xchk_update_health`
- `xchk_ag_btree_del_cursor_if_sick`
- `xchk_mark_healthy_if_clean`
- `xchk_file_looks_zapped`
- `xchk_health_record`

Purpose:
- Provides the interface for scrub modules to map scrub outcomes to incore XFS sick/healthy state.
- Also exposes cross-reference cursor pruning for already sick AG btrees.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/health.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc.c

This file scrubs the inode allocation btrees: inobt and finobt. It validates record geometry, sparse inode masks, inode cluster contents, free/allocated state, and cross-references against each other and the rmap btree.

Setup:
- `xchk_setup_ag_iallocbt` enables intent draining when needed and then sets up AG btree scrub. Try-harder mode affects setup behavior.

Scrub state:
- `struct xchk_iallocbt` tracks total inodes observed and expected record sequencing for large cluster geometries.

Record checks:
- `xchk_iallocbt_rec` converts btree records to incore form, validates with `xfs_inobt_check_irec`, checks alignment, counts inodes, handles sparse and non-sparse records, and validates clusters.
- `xchk_iallocbt_rec_alignment` enforces inobt and finobt alignment rules, including multi-record inode clusters.
- `xchk_iallocbt_chunk` validates block ranges, checks used-space ownership, cross-references peer btrees, and rejects shared/COW staging ownership.

Inode cluster checks:
- `xchk_iallocbt_check_cluster` maps each inode cluster buffer, validates holemask consistency, checks rmap ownership, and reads cluster buffers.
- `xchk_iallocbt_check_cluster_ifree` compares inobt free bits with incore inode allocation state or on-disk `di_mode` fallback.

Inobt/finobt cross-reference:
- `xchk_inobt_xref_finobt` and `xchk_finobt_xref_inobt` compare free/hole state one inode at a time.
- Finobt may omit records for fully allocated, fully free, or hole-only cases as documented in the code.

Rmap cross-reference:
- `xchk_iallocbt_xref_rmap_btreeblks` verifies rmap-owned inobt/finobt btree block counts.
- `xchk_iallocbt_xref_rmap_inodes` verifies inode chunk blocks seen in inobt match rmap `OWN_INODES`.

Exported xref helpers:
- `xchk_xref_is_not_inode_chunk`
- `xchk_xref_is_inode_chunk`

Risks and edge cases:
- Incore-vs-disk inode state can require `-EDEADLOCK` if try-harder was not requested.
- Sparse inode holemask validation must match cluster allocation exactly.
- Corrupt peer btree cursors can be dropped through scrub xref handling, limiting follow-on checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc_repair.c

This file repairs the inode allocation btrees by rebuilding both inobt and finobt from reverse mapping records and inode cluster contents.

Core repair model:
- Requires rmapbt support.
- Walks rmap records for `OWN_INODES` and `OWN_INOBT`.
- Reconstructs inode records from inode cluster buffers.
- Bulk-loads new inobt and finobt trees.
- Commits new roots to the AGI and reaps old btree blocks.

Key state:
- `struct xrep_ibt` holds the current reconstructed inode record, two `xrep_newbt` builders, a bitmap of old inode btree blocks, an `xfarray` of reconstructed records, counters, and array cursor state.

Record reconstruction:
- `xrep_ibt_record_inode_blocks` validates inode rmap extents and processes each cluster.
- `xrep_ibt_process_cluster` directly maps inode cluster buffers without using the damaged inobt.
- `xrep_ibt_cluster_record` builds inobt records, computes hole/free masks, counts inodes, and tracks finobt record needs.
- `xrep_ibt_check_ifree` determines inode in-use state from incore allocation state or on-disk dinode mode.

Validation:
- `xrep_ibt_check_inode_ext` checks AG extent validity, cluster alignment, sparse inode alignment, valid inode number range, and absence from free-space btrees.
- `xrep_ibt_check_overlap` ensures reconstructed records are ordered and non-overlapping.

Tree rebuild:
- `xrep_ibt_build_new_trees` stages fake roots, computes bload geometry, reserves blocks, bulk-loads inobt and optional finobt, commits roots into AGI, resets AGI counters, commits new reservations, and rolls the AG transaction.
- `xrep_ibt_get_records` feeds all records to inobt.
- `xrep_fibt_get_records` feeds only records with free inodes to finobt.
- `xrep_ibt_remove_old_trees` reaps old inode btree blocks and requests per-AG reservation reset when needed.

Public entry points:
- `xrep_iallocbt` rebuilds both inode btrees and sets `sc->sick_mask` to cover both inobt and finobt.
- `xrep_revalidate_iallocbt` reruns scrub for inobt and, if enabled, finobt after repair.

Important invariants:
- Repair locks AGI through scrub setup, preventing concurrent inode allocation/free changes.
- Both trees are rebuilt together because they share rmap ownership and record source data.
- Old btrees become inaccessible only after staged roots are committed.

Risks and edge cases:
- ENOSPC can occur while reserving replacement btree blocks.
- If finobt revalidation loses its cursor, repair is marked incomplete.
- Bad rmap data prevents repair because rmap is the source of truth.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/ialloc_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/ino_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/ino_bitmap.h

This header provides a type-specific wrapper around `xbitmap64` for inode numbers.

Key definition:
- `struct xino_bitmap` contains an `xbitmap64 inobitmap`.

Provided helpers:
- `xino_bitmap_init`
- `xino_bitmap_destroy`
- `xino_bitmap_set`
- `xino_bitmap_test`

Purpose:
- Stores individual `xfs_ino_t` values in a 64-bit bitmap abstraction.
- `xino_bitmap_set` records one inode at a time.
- `xino_bitmap_test` checks whether one inode is present by testing a length-one range.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/ino_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/inode.c

This file scrubs inode core metadata. It handles setup for live inode or by-handle inode scrubs, detects corrupt-on-load inodes, validates dinode fields, and cross-references inode state against allocation metadata and mappings.

Setup paths:
- `xchk_setup_inode` handles three cases:
  - scrub the open file’s inode
  - safely load a requested inode by handle
  - if iget fails due to corruption, lock AGI, verify inobt allocation, save imap for repair, and let `xchk_inode` report corruption
- Metadata directory non-directory inodes are rejected from direct userspace by-handle scrub.
- Internal sb-rooted metadata files are rejected on pre-metadir filesystems.

Core validation:
- `xchk_dinode` validates mode, inode version, metadir type, project id fields, UID/GID warnings, fork formats, timestamps, size, nblocks, flags, extent hints, fork offsets, attr format, and extent counters.
- `xchk_inode_flags` checks legacy di_flags against mode and feature constraints.
- `xchk_inode_flags2` checks reflink, DAX, bigtime, large extent count, and realtime/reflink compatibility.
- `xchk_inode_extsize` and `xchk_inode_cowextsize` validate extent size hints and issue warnings for admin-created realtime hint misalignment.

Cross-reference checks:
- `xchk_inode_xref` initializes AG metadata and verifies the inode block is used, finobt does not mark it free, rmap says it is inode-owned, and it is not shared or COW staging.
- `xchk_inode_xref_bmap` recounts fork extents/blocks and compares them with dinode counters.
- `xchk_inode_check_reflink_iflag` compares reflink flag state with shared extent discovery.
- `xchk_inode_check_unlinked` checks link count against the incore unlinked list.

Main scrub:
- `xchk_inode` marks corruption if setup could not load `sc->ip`, otherwise converts the incore inode to a disk dinode image, validates it, optionally checks reflink and unlinked state, and performs xrefs.

Important invariants:
- Inode scrub holds IOLOCK and ILOCK exclusively after setup.
- Inobt allocation status is trusted for detecting allocated-but-unloadable inodes.
- Warnings are used for suspicious but historically possible admin/user values.

Risks and edge cases:
- Some corrupt inodes cannot be loaded; repair must use the saved imap in `inode_repair.c`.
- Reflink nblocks can legitimately exceed physical block count.
- Realtime, metadir, and feature-gated formats require special validation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/inode_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/inode_repair.c

This file repairs inode record problems. It has two major regimes: raw dinode repair for inodes that cannot pass verifiers and be loaded, followed by live incore inode repair once `iget` succeeds.

Repair state:
- `struct xrep_inode` stores the saved `xfs_imap`, scrub context, block/extent counts discovered from rmap, sick masks for zapped metadata, ACL-zap state, and an inode scanner used to infer file type from directory entries.

Raw dinode repair:
- `xrep_setup_inode` stores the imap from setup when `iget` failed.
- `xrep_dinode_buf_core` and `xrep_dinode_buf` repair inode cluster buffer verifier requirements: magic, version, next-unlinked field, and CRC.
- `xrep_dinode_header` repairs invariant inode fields such as magic, version, inode number, UUID, and generation.
- `xrep_dinode_find_mode` scans directories with `xchk_iscan` to infer file type from dirent ftypes when mode bits are garbage.
- `xrep_dinode_mode` converts unrecognized modes to a conservative root-owned file type and marks ACLs for zapping.

Fork and size repair:
- `xrep_dinode_count_rmaps` counts this inode’s data, realtime, and attr blocks/extents from data-device and realtime rmap btrees.
- `xrep_dinode_check_dfork` and `xrep_dinode_check_afork` detect fork formats that would fail ifork verifiers or formatters.
- `xrep_dinode_zap_dfork` resets bad data forks to a safe format and marks bmbtd zapped.
- `xrep_dinode_zap_afork` empties attr forks, removes access permissions, clears IDs, and marks bmbta zapped.
- `xrep_dinode_zap_symlink` and `xrep_dinode_zap_dir` create minimal salvage structures for invalid local symlinks/directories.
- `xrep_dinode_ensure_forkoff` adjusts fork layout so later bmap repair can recreate mappings when rmap found extents.
- `xrep_dinode_core` writes the repaired raw dinode, retries `iget`, commits the transaction, attaches quota state, locks the live inode, and marks zapped sick flags.

Live inode repair:
- `xrep_inode_blockcounts` recounts fork mappings and updates extent counts and `i_nblocks`.
- `xrep_inode_ids` repairs invalid UID/GID/project IDs and schedules quotacheck when quotas are enabled.
- `xrep_inode_timestamps` clamps invalid nanoseconds.
- `xrep_inode_flags` clears impossible flag combinations.
- `xrep_inode_dir_size` derives directory size from extents or shortform data.
- `xrep_inode_pptr` ensures parent-pointer-capable files have an attr fork when required.
- `xrep_inode_extsize` and `xrep_inode_cowextsize` clear invalid realtime-related extent hints.
- `xrep_inode_unlinked` reconciles link count with the incore unlinked list.

Main entry:
- `xrep_inode` first repairs raw dinode verifier failures if `sc->ip` is absent, then joins the live inode to the transaction, repairs corrupt fields, clears reflink flags when possible, reconnects unlinked list state, and finishes deferred work.

Important invariants:
- Raw repair is conservative and may intentionally zap damaged forks so higher-level bmap, dir, symlink, or xattr repair can recover later.
- Rmapbt is required for reconstructing block and extent counts during raw repair.
- Bad ACL-bearing attr forks cause permissions and ownership to be restricted.

Risks and edge cases:
- Directory scans to infer mode can return busy; the repair defers rather than forcing unsafe progress.
- If data and realtime extents both exist for one inode, repair treats that as corruption.
- Zapping forks can temporarily leak or orphan metadata until follow-up repair phases run.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/inode_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.c

This file implements live filesystem inode scanning for scrub and repair modules that need to visit every allocated inode while concurrent updates may occur.

Core model:
- The scanner walks allocated inodes from the inobt while holding AGI during cursor advancement.
- It records a scan start, current cursor, visited cursor, skipped inode mask, and batched inode references.
- Callers pair scanning with live update hooks and use `xchk_iscan_want_live_update` to decide whether an update applies to already-scanned ranges.

Cursor advancement:
- `xchk_iscan_find_next` uses an inobt cursor to find the next allocated inode after the scan cursor, masks `skip_ino`, and returns an allocation mask for a chunk.
- `xchk_iscan_move_cursor` updates scan and visited cursors while holding the scanner mutex.
- `xchk_iscan_advance` reads AGI, finds the next inode, wraps across AGs, and marks the scan finished when it returns to the start.
- `xchk_iscan_finish` and `xchk_iscan_finish_early` mark all future updates as applicable.

Inode acquisition:
- `xchk_iscan_read_agi` optionally trylocks AGI with retry timing.
- `xchk_iscan_iget` gets the first inode and then attempts to batch up to a chunk of consecutive allocated inodes with no-retry/dontcache flags.
- `xchk_iscan_iget_retry` backs up the cursor after transient iget failures, optionally pushing or flushing inodegc.
- `xchk_iscan_iter_batch` advances and fills a batch.
- `xchk_iscan_iter` hands one inode reference to the caller.
- `xchk_iscan_iter_finish` drops leftover batched references.

Live update selection:
- `xchk_iscan_mark_visited` marks an inode fully scanned.
- `xchk_iscan_finish_batch` advances visited state over skipped unallocated inodes.
- `xchk_iscan_skipped` identifies newly allocated inodes skipped in the current batch.
- `xchk_iscan_want_live_update` returns true for finished scans, skipped inodes, or inodes within the already visited range, handling wraparound.

Startup and teardown:
- `xchk_iscan_start` chooses a rotating AG start point, initializes timing, state, mutex, cursors, and batch slots.
- `xchk_iscan_teardown` releases batched references, marks finished, and destroys the mutex.

Important invariants:
- Cursor advancement under AGI prevents inode create/delete races across the advanced range.
- Callers must hold adequate inode locks before calling `xchk_iscan_mark_visited`.
- Skipped unallocated inodes must receive live updates because they can be allocated after the batch snapshot.

Risks and edge cases:
- Inodegc races can cause temporary `-EAGAIN`, `-ENOENT`, or `-EBUSY`.
- Trylock AGI mode lets repair avoid deadlocks when already holding locks such as AGI elsewhere.
- Aborted scans suppress live updates.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.h

This header defines the live inode scanner state and public API.

Key structure:
- `struct xchk_iscan`
  - scrub context
  - mutex-protected scan cursors
  - optional `skip_ino`
  - operation bits for aborted scans and AGI trylock mode
  - iget timeout/retry fields
  - batch base inode, skipped mask, and inode reference array

Operation bits:
- `XCHK_ISCAN_OPSTATE_ABORTED`
- `XCHK_ISCAN_OPSTATE_TRYLOCK_AGI`

Inline helpers:
- `xchk_iscan_aborted`
- `xchk_iscan_abort`
- `xchk_iscan_agi_needs_trylock`
- `xchk_iscan_set_agi_trylock`

Exported API:
- Start, finish early, teardown.
- Iterate and finish iteration.
- Mark an inode visited.
- Query whether a live update should be applied.

Integration:
- Used by parent finding, inode repair mode inference, and any scrub/repair code that builds metadata from a live full-inode scan.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.c

This file provides a scrub-safe extended attribute walker. It calls caller-provided callbacks for every xattr entry in shortform, leaf, or node-format attr forks.

Shortform path:
- `xchk_xattr_walk_sf` iterates in-core shortform entries and calls `attr_fn` with flags, name, value pointer, and lengths.

Leaf path:
- `xchk_xattr_walk_leaf` reads attr leaf block zero and calls `xchk_xattr_walk_leaf_entries`.
- `xchk_xattr_walk_leaf_entries` decodes each leaf entry, distinguishes local vs remote values, passes local values directly, and passes `NULL` for remote values while preserving remote value length.

Node path:
- `xchk_xattr_find_leftmost_leaf` descends the dabtree from block zero to the leftmost leaf, checking node/leaf magic, headers, levels, and loops with an `xdab_bitmap`.
- `xchk_xattr_walk_node` walks leaf sibling links from left to right, invokes `leaf_fn` between leaves if provided, and detects leaf loops with the bitmap.

Public API:
- `xchk_xattr_walk` requires the inode ILOCK, returns immediately if no attrs exist, handles shortform directly, reads attr fork extents for non-local formats, and selects leaf vs node walking.

Important invariants:
- No cursor restarts are allowed; callers must hold ILOCK.
- Any structural problem, including dabtree loops, returns `-EFSCORRUPTED`.
- Remote attr values are not read here; callers receive metadata and length only.

Risks and edge cases:
- Node format traversal validates only enough structure to walk safely and detect loops.
- Callback errors stop traversal immediately.
- The optional `leaf_fn` gives callers a per-leaf boundary hook for stateful scrub logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.h

This header declares callback types and the xattr walker used by scrub code.

Types:
- `xchk_xattr_fn`: called per xattr entry with scrub context, inode, attr flags, name, name length, value pointer, value length, and private data.
- `xchk_xattrleaf_fn`: optional callback invoked around leaf traversal in node-format attr forks.

Exported function:
- `xchk_xattr_walk`

Purpose:
- Provides a uniform interface over shortform, leaf, and node-format extended attributes without requiring each scrubber to duplicate attr fork traversal logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/metapath.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/metapath.c

This file scrubs and repairs metadata directory paths. On metadir-enabled filesystems, certain metadata files must be reachable by fixed names under the metadata directory tree; this file verifies and restores those links.

State:
- `struct xchk_metapath` tracks the scrub context, final path component, directory update state, parent directory inode, lock flags, transaction reservations, parent pointer args, and scratch args for removing parent pointers.

Setup:
- `xchk_setup_metapath` accepts metapath selectors in `sm_ino`, rejects non-metadir filesystems and invalid generations, and installs the metadata inode and expected parent/path.
- Runtime feature blocks support realtime metadata paths under `rtgroups` and quota metadata under `quota`.
- Probe mode validates inputs without installing a target.

Scrub:
- `xchk_metapath` allocates an empty transaction, locks parent and child, looks up the expected name in the parent directory, and marks corruption if the dirent is missing or points to the wrong inode.

Repair:
- `xrep_metapath` ensures parent pointer storage if needed, computes link/unlink reservations, then loops:
  - `xrep_metapath_try_link` creates the correct dirent if absent, accepts existing correct links, or reports the wrong child.
  - `xrep_metapath_try_unlink` removes the wrong dirent, including parent pointer cleanup when present, and handles races where the dirent changes.
- `xrep_metapath_link` and `xrep_metapath_unlink` wrap XFS directory child add/remove operations.

Locking:
- `xchk_metapath_ilock_both` locks parent and trylocks child to avoid deadlocks when metadata directories may be corrupt.
- `xchk_metapath_ilock_parent_and_child` does the same for an alleged wrong child during repair.

Important invariants:
- Repair must run after other repairs because it creates transactions and takes ILOCKs.
- Parent directory is required for non-probe scrub/repair.
- Parent pointer updates are conditional on filesystem parent-pointer support.

Risks and edge cases:
- Wrong-child removal handles bogus or unallocated inode numbers by junking the dirent.
- Concurrent changes can return `-EAGAIN` and update the alleged child for retry.
- Missing quota or realtime metadata inodes produce `-ENOENT` at setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/metapath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.c

This file is the common helper for online repair code that builds a replacement btree. It manages block reservations, fake-root staging, allocation hints, bulk-loader block claiming, commit cleanup, and cancellation cleanup.

Initialization:
- `xrep_newbt_init_ag` initializes an AG btree builder with owner info, allocation hint, reservation type, reservation list, bload dirty limit, and slack estimates.
- `xrep_newbt_init_inode` initializes an inode-fork btree builder with a fake ifork.
- `xrep_newbt_init_metadir_inode` initializes a metadata inode btree builder with bmbt owner info and regular block allocation semantics.
- `xrep_newbt_init_bare` initializes a builder without automatic reservations.

Slack policy:
- `xrep_newbt_estimate_slack` uses default bulk-load slack unless debug knobs override it.
- If free space is below 10 percent for the relevant scope, it tightens leaf/node slack to reduce repair space usage.

Reservation and allocation:
- `xrep_newbt_add_blocks` records a reserved extent, holds the perag, and schedules autoreap when allocated in the transaction.
- `xrep_newbt_add_extent` manually adds caller-supplied blocks without autoreap.
- `xrep_newbt_alloc_ag_blocks` allocates blocks within the current AG.
- `xrep_newbt_alloc_file_blocks` allocates file-based btree blocks across the filesystem.
- `xrep_newbt_alloc_blocks` selects AG vs file allocation based on whether `sc->ip` is set.

Commit and cancel:
- `xrep_newbt_free_extent` either commits autoreap for cancelled/unused allocations or cancels autoreap and frees unused tail blocks after a committed btree.
- `xrep_newbt_free` walks all reservations, logs deferred frees in bounded batches, frees perag references, and frees fake iforks.
- `xrep_newbt_commit` frees only unused reservation space after a successful btree commit.
- `xrep_newbt_cancel` rolls back all reserved blocks for an abandoned replacement tree.

Bulk loading:
- `xrep_newbt_claim_block` hands one reserved block to the btree bulk loader, advances `used`, rotates exhausted reservations, fills short or long btree pointers, and finishes deferred work to relog EFIs.
- `xrep_newbt_unused_blocks` reports unused reserved blocks.

Important invariants:
- AG btree allocation must remain in the scrubbed AG.
- File btree allocation validates hints against EOFS.
- `XREP_MAX_ITRUNCATE_EFIS` limits deferred free items before rolling/finishing deferred work.
- Reservations are protected with autoreap so failures do not leak blocks where possible.

Risks and edge cases:
- Filesystem shutdown skips block freeing and only cleans incore tracking.
- ENOSPC during allocation or claiming blocks cancels the staged tree.
- Metadir inode btree repair accepts higher ENOSPC risk because metadata reservations cannot be charged until commit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.h

This header declares the replacement-btree builder used by online repair.

Key structures:
- `struct xrep_newbt_resv`
  - reservation list link
  - perag reference
  - autoreap state
  - AG block start, length, and used count
- `struct xrep_newbt`
  - scrub context
  - optional custom allocator
  - reservation list
  - fake AG or inode btree root
  - rmap owner info
  - btree bulk-load geometry
  - allocation hint
  - per-AG reservation type

Exported operations:
- Initialize for bare, AG, inode, or metadir inode use.
- Allocate blocks or add a known extent.
- Cancel or commit reservations.
- Claim a block for btree bulk loading.
- Query unused blocks.

Integration:
- Used by repair modules that rebuild btrees into staged fake roots before atomically committing new roots.
- Exposes enough hooks for callers to plug custom allocation and bload record providers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/newbt.h -->