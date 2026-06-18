# Group Research: group_865_linux_sources_os_linux_linux_fs_xfs_scrub_findparent_c_sources_os_li_a64206ccb063

Scope: `Docs/research_subset_a.md`

This grouped report covers the listed Linux XFS online scrub and repair files under `sources/os/linux/linux/fs/xfs/scrub`. The files focus on parent discovery, filesystem counter checking/repair, health state updates, inode allocation btree scrub/repair, inode core scrub/repair, live inode scanning, xattr walking, metadata-directory path checking/repair, and new-btree staging utilities.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/findparent.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/findparent.c

Implements support for finding and validating the parent directory of a directory being repaired. XFS directories have a `..` parent relationship, but repair sometimes must reconstruct or verify it by scanning the directory tree for a non-dot dirent that points to the target inode.

Main components:
- `struct xrep_findparent_info` tracks the directory currently being scanned, the scrub target, optional live parent-scan state, a discovered parent inode, and whether that parent is tentative.
- `xrep_findparent_dirent` is the dirent callback. It ignores non-target entries, rejects invalid names, ignores `.` and `..`, detects multiple parent candidates, records the found parent, and updates parent-scan state.
- `xrep_findparent_walk_directory` locks a candidate directory’s data map, rejects the target itself, temporary repair inodes, mismatched metadata-vs-normal directory trees, sick directories, and zapped directories, then walks dirents.
- `xrep_findparent_live_update` is a directory-update hook used during full scans. If a dirent update affects the scrub target and the parent directory has already been scanned, it updates the scan result.
- `__xrep_findparent_scan_start`, `xrep_findparent_scan`, `xrep_findparent_scan_teardown`, and `xrep_findparent_scan_finish_early` coordinate a live inode scan plus dirent hook so filesystem-wide parent discovery remains valid while directory updates continue.
- `xrep_findparent_confirm` validates a proposed parent by checking root/metadir/unlinked special cases, rejecting bogus or self-referential parent inode numbers, igetting the parent, and confirming it contains a child dirent for the target.
- `xrep_findparent_self_reference` handles directory-tree roots and unlinked directories without scanning.
- `xrep_findparent_from_dcache` queries the VFS dcache for a likely parent as an optimization.

Key invariants:
- Parent discovery cannot hold the target inode ILOCK for the entire filesystem scan, so live dirent hooks are required.
- Metadata directory trees and user directory trees must not be mixed.
- Directories known sick or zapped are not trusted as scan inputs.
- Multiple non-dot parent dirents for one directory are corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/findparent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/findparent.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/findparent.h

Defines the public parent-scan state and entry points used by directory parent repair.

Main declarations:
- `struct xrep_parent_scan_info` stores the scrub context, `xchk_iscan` cursor, dirent hook, mutex-protected discovered parent inode, and a `lookup_parent` flag.
- `__xrep_findparent_scan_start` starts a scan with an optional custom notifier.
- `xrep_findparent_scan_start` wraps the custom start helper with the default live-update hook.
- `xrep_findparent_scan`, `xrep_findparent_scan_teardown`, and `xrep_findparent_scan_finish_early` run and manage scan lifetime.
- `xrep_findparent_scan_found` updates `parent_ino` under mutex.
- `xrep_findparent_confirm`, `xrep_findparent_self_reference`, and `xrep_findparent_from_dcache` expose confirmation and shortcut helpers.

The header couples parent repair to live inode scanning and dirent hook infrastructure while keeping parent result mutation serialized.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/findparent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fsb_bitmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/fsb_bitmap.h

Provides a typed wrapper around the generic 64-bit scrub bitmap for filesystem block numbers.

Main API:
- `struct xfsb_bitmap` embeds `struct xbitmap64`.
- `xfsb_bitmap_init` and `xfsb_bitmap_destroy` manage bitmap lifetime.
- `xfsb_bitmap_set` records a filesystem-block range using `xfs_fsblock_t` and `xfs_filblks_t`.
- `xfsb_bitmap_walk` iterates set ranges with the generic 64-bit walk callback type.

This wrapper gives callers type-specific names for filesystem-block tracking while reusing the interval-tree bitmap implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fsb_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fscounters.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/fscounters.c

Scrubs global filesystem summary counters: inode count, free inode count, free data blocks, and free realtime extents. It recomputes expected values from per-AG/per-RT metadata and compares those values to in-core percpu counters, with tolerance for live filesystem activity unless repair or try-harder mode freezes the filesystem.

Main flow:
- `xchk_fscount_warmup` walks AGs and reads AGI/AGF headers as needed so per-AG in-core counters are initialized before fast aggregation.
- `xchk_fsfreeze`, `xchk_fsthaw`, `xchk_fscounters_freeze`, and `xchk_fscounters_cleanup` manage kernel freeze/thaw for stable counter checking or repair.
- `xchk_setup_fscounters` allocates `struct xchk_fscounters`, computes legal inode-count range, warms per-AG state, optionally freezes the filesystem, and starts an empty transaction.
- `xchk_fscount_btreeblks` manually counts free-space btree blocks for filesystems without lazy superblock counters.
- `xchk_fscount_aggregate_agcounts` sums per-AG inode/free/freeblock counters, btree blocks, freelist blocks, and subtracts per-AG reservations, global reservation, and delayed allocation reservations.
- `xchk_fscount_count_frextents` counts free realtime extents from rt bitmap data when applicable; the non-RT build returns zero counts.
- `xchk_fscount_within_range` compares expected values to before/after percpu counter snapshots. Exact matches are required for repair; non-repair scans tolerate expected values between the two snapshots.
- `xchk_fscounters` snapshots counters, rejects impossible values, recomputes expected counts, compares each counter, marks corruption if frozen and mismatched, or returns `-EDEADLOCK` to request a retry with stronger protection.

Important behavior:
- Lockless aggregation can race with live allocation, so non-frozen mismatches are treated as retryable when plausible.
- Incomplete aggregation must set `INCOMPLETE` to prevent repair from using insufficient data.
- Zoned realtime filesystems skip frextents verification because their counters include reservations differently.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fscounters.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fscounters.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/fscounters.h

Defines `struct xchk_fscounters`, the shared scrub/repair state for filesystem summary counters.

Fields:
- `sc`: owning scrub context.
- `icount`, `ifree`, `fdblocks`: recomputed global inode, free inode, and free data-block counts.
- `frextents`, `frextents_delayed`: recomputed free realtime extent count and delayed realtime extent reservations.
- `icount_min`, `icount_max`: legal inode-count bounds.
- `frozen`: whether setup froze the filesystem and cleanup must thaw it.

This state is filled by scrub and consumed by `fscounters_repair.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fscounters.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fscounters_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/fscounters_repair.c

Repairs filesystem summary counters by resetting in-core counters to values computed during the required scrub phase.

Main function:
- `xrep_fscounters` requires `fsc->frozen` to be true, traces the reset, sets `m_icount`, `m_ifree`, and free block counters from scrub-computed values, and updates realtime free extent counters when appropriate.

Important details:
- Repair depends on the setup/check phase freezing the filesystem, preventing concurrent counter changes.
- Online repair only supports v5 filesystems with lazy data-block superblock counters, so it does not update `sb_fdblocks` directly.
- `sb_frextents` is updated directly for non-rtgroup realtime filesystems because its lazy-counter behavior differs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/fscounters_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/health.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/health.c

Maps scrub results to XFS in-core health state. Scrub and repair can perform cross-structure validation, so this file updates filesystem, AG, inode, and realtime-group sickness flags based on scrub outcomes.

Main components:
- `enum xchk_health_group` identifies whether a scrub type maps to no object, filesystem, AG, inode, or realtime group health.
- `type_to_health_flag` maps each scrub type to its health group and sickness mask.
- `xchk_health_mask_for_scrub_type` returns the default sickness mask.
- `xchk_mark_healthy_if_clean` adds extra health bits to clear if the scrub result stayed clean.
- `xchk_file_looks_zapped` detects pre-existing zapped inode metadata while allowing post-repair revalidation.
- `xchk_mark_all_healthy` clears indirect filesystem, AG, and realtime-group health markers after a clean whole-filesystem health scan.
- `xchk_update_health` is the central updater. It sets direct sickness flags on corrupt results and clears masks on clean results, with special handling for repair and the `HEALTHY` scrub type.
- `xchk_ag_btree_del_cursor_if_sick` discards cross-reference cursors for known-sick AG btrees, setting `XFAIL` instead of trusting them.
- `xchk_health_record` checks for any remaining primary sickness in filesystem, AG, or realtime-group health records.

Key policy:
- Runtime errors do not update health.
- Clean scans clear the relevant sick flags.
- Corrupt scans set them.
- Repairs that rebuild multiple structures must expand the sick mask so all rebuilt structures are revalidated and updated together.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/health.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/health.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/health.h

Declares the scrub health-state helpers:
- `xchk_health_mask_for_scrub_type`
- `xchk_update_health`
- `xchk_ag_btree_del_cursor_if_sick`
- `xchk_mark_healthy_if_clean`
- `xchk_file_looks_zapped`
- `xchk_health_record`

This header exposes the bridge between scrub result flags and XFS health accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/health.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/ialloc.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/ialloc.c

Scrubs the inode allocation btrees: inobt and finobt. It validates btree records, sparse inode hole masks, free masks, inode cluster buffers, alignment rules, and cross-references with the other inode btree plus rmap/free/refcount state.

Main components:
- `xchk_setup_ag_iallocbt` enables intent draining when needed and sets up AG btree scrub.
- `struct xchk_iallocbt` tracks scanned inode count and expected sequencing for geometries where one inode cluster spans multiple inobt records.
- `xchk_inobt_xref_finobt` and `xchk_finobt_xref_inobt` compare per-inode free/hole state between inobt and finobt, accounting for finobt omission rules.
- `xchk_iallocbt_chunk` validates the block range for a chunk, verifies it is used inode space, cross-references the opposite btree, rmap ownership, sharing, and CoW staging.
- `xchk_iallocbt_check_cluster_ifree` compares each inode’s allocation state from icache or disk against the inobt free mask.
- `xchk_iallocbt_check_cluster` validates cluster-level holemask consistency, maps the inode cluster buffer, and checks all contained dinodes.
- `xchk_iallocbt_rec_alignment` enforces inobt/finobt record alignment rules, including multi-record clusters.
- `xchk_iallocbt_rec` converts and validates a btree record, handles sparse/non-sparse records, checks hole/free count consistency, then checks clusters.
- `xchk_iallocbt_xref_rmap_btreeblks` compares counted inobt/finobt blocks with rmap-owned inode-btree blocks.
- `xchk_iallocbt_xref_rmap_inodes` compares inode blocks implied by inobt records with rmap-owned inode blocks.
- `xchk_iallocbt` selects the correct cursor, runs generic btree scrub, and performs rmap cross-references.
- `xchk_xref_is_not_inode_chunk` and `xchk_xref_is_inode_chunk` provide extent-to-inode-btree cross-reference helpers for other scrubbers.

Important invariants:
- Inobt must cover allocated inode chunks; finobt only tracks chunks with free inodes and can omit fully allocated/fully free/hole-only cases.
- Sparse inode holemask bits must map whole cluster subranges.
- Dinode magic and v3 inode number must match the btree-implied inode.
- Inode chunk space must be owned only by inode rmap records, not shared, and not CoW staging.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/ialloc_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/ialloc_repair.c

Rebuilds both inode allocation btrees for an AG from reverse mapping data. The repair is coupled because inobt and finobt share the same rmap owner and are easier to reconstruct together from inode cluster state.

Main flow:
- `struct xrep_ibt` tracks the record under construction, new inobt/finobt staging state, old btree blocks, reconstructed records in an `xfarray`, inode/free counts, finobt record count, and array cursor state.
- `xrep_ibt_check_ifree` determines whether an inode is in use from icache or disk dinode state.
- `xrep_ibt_cluster_record` builds/updates the reconstructed inobt record for an inode cluster, maintaining count, holemask, and freemask.
- `xrep_ibt_process_cluster` reads an inode cluster buffer directly and processes each possible inobt record covered by the cluster.
- `xrep_ibt_check_inode_ext` validates rmap-owned inode extents for AG bounds, cluster alignment, sparse/non-sparse alignment, inode-number validity, and not-free-space status.
- `xrep_ibt_walk_rmap` collects old inode btree blocks (`OWN_INOBT`) and inode cluster extents (`OWN_INODES`).
- `xrep_ibt_find_inodes` walks all AG rmaps and stashes the final reconstructed record.
- `xrep_ibt_reset_counters` updates AGI inode/free counters and reinitializes per-AG state.
- `xrep_ibt_get_records` and `xrep_fibt_get_records` feed reconstructed inobt and finobt records to the btree bulk loader.
- `xrep_ibt_build_new_trees` checks record overlap, stages new fake-root btrees, computes geometry, reserves blocks, bulk-loads records, commits new roots to AGI, resets counters, and commits reservations.
- `xrep_ibt_remove_old_trees` reaps old inode-btree blocks and requests per-AG reservation reset when needed.
- `xrep_iallocbt` requires rmapbt, allocates repair state, expands `sick_mask` to both inobt and finobt, builds records, installs new trees, and reaps old trees.
- `xrep_revalidate_iallocbt` temporarily changes scrub type to re-scrub inobt and finobt in the correct cross-reference direction.

Key invariants:
- Repair depends on rmapbt; without rmap ownership data it returns `-EOPNOTSUPP`.
- AGI locking protects against concurrent inode allocation/free while rebuilding.
- Records are collected in increasing AG inode order and checked for overlap before loading.
- Old trees are not reaped until new roots have been committed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/ialloc_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/ino_bitmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/ino_bitmap.h

Provides a typed single-inode bitmap wrapper around the generic 64-bit bitmap.

Main API:
- `struct xino_bitmap` embeds `struct xbitmap64`.
- `xino_bitmap_init` and `xino_bitmap_destroy` manage lifetime.
- `xino_bitmap_set` records one `xfs_ino_t`.
- `xino_bitmap_test` tests whether one inode number is present.

This is used where scrub/repair needs sparse tracking of individual filesystem inode numbers without exposing raw 64-bit bitmap calls.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/ino_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/inode.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/inode.c

Scrubs inode core metadata. Setup carefully obtains a live inode or, if iget fails due to corruption, preserves enough AGI and inode mapping state for repair to fix the on-disk inode buffer.

Main flow:
- `xchk_prepare_iscrub` takes IOLOCK, allocates transaction, attaches dquots, and takes ILOCK.
- `xchk_install_handle_iscrub` installs a scrub-by-handle inode, rejects unsafe non-directory metadata-dir files from userspace, and prepares it.
- `xchk_setup_inode` handles opened-inode scrubs, scrub-by-handle validation, safe untrusted iget, retry under AGI lock, direct inobt mapping via `xfs_imap`, and repair setup for allocated but unloadable corrupt inodes.
- `xchk_dinode` validates dinode fields: mode, version, metatype, project ID support, uid/gid warnings, fork format, timestamps, size, nblocks, flags, extsize/cowextsize hints, nextents/anextents, forkoff, attr format, bigtime, and large extent count feature dependencies.
- `xchk_inode_xref_finobt` ensures finobt does not mark the loaded inode free.
- `xchk_inode_xref_bmap` compares fork extent counts and block counts against inode core counters.
- `xchk_inode_xref` checks backing block usage, finobt, rmap ownership, sharing, CoW staging, and fork counters.
- `xchk_inode_check_reflink_iflag` compares the reflink inode flag to actual shared data fork extents, marking preen or corruption.
- `xchk_inode_check_unlinked` verifies link count matches unlinked-list membership.
- `xchk_inode` converts the live inode to a disk-format dinode for checking, handles setup-detected unloadable corruption, performs reflink/unlinked checks, and cross-references.

Important behavior:
- Setup returns `-ENOENT` for free/missing inodes so scrub can skip them.
- If inobt says an inode is allocated but iget fails from corruption, setup leaves state for repair rather than marking corruption directly.
- Cross-reference checks are skipped after primary inode corruption to avoid noisy secondary reports.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/inode_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/inode_repair.c

Repairs inode records. It has two layers: raw dinode repair for verifier-failing inodes that cannot be loaded, and incore inode repair for inconsistencies that can be fixed after iget succeeds.

Main raw-dinode repair:
- `struct xrep_inode` stores saved `xfs_imap`, rmap-derived block/extent counts, sick bits to set after zapping, ACL-zap state, and scan state for recovering file type from directory entries.
- `xrep_setup_inode` saves the inode mapping produced by scrub setup.
- `xrep_dinode_buf_core` and `xrep_dinode_buf` fix inode-buffer verifier essentials: magic, version, CRC, and next-unlinked validity.
- `xrep_dinode_header` resets immutable header fields: magic, version, inode number, UUID, and generation.
- `xrep_dinode_find_mode` scans directories with `xchk_iscan` to infer file type from dirents when `di_mode` is garbage.
- `xrep_dinode_mode`, `xrep_dinode_nlinks`, `xrep_dinode_flags`, `xrep_dinode_size`, and `xrep_dinode_extsize_hints` repair verifier-sensitive core fields.
- `xrep_dinode_count_rmaps` scans data and realtime rmaps to infer blocks/extents owned by the inode.
- `xrep_dinode_check_dfork` and `xrep_dinode_check_afork` validate fork format and embedded fork contents enough for ifork verifiers.
- `xrep_dinode_zap_dfork`, `xrep_dinode_zap_afork`, `xrep_dinode_zap_symlink`, and `xrep_dinode_zap_dir` reset unrecoverable forks to safe minimal structures and mark zapped sickness.
- `xrep_dinode_ensure_forkoff` adjusts fork offset so existing/recoverable data and attr fork stubs can fit.
- `xrep_dinode_core` reads the inode cluster, fixes the raw dinode, writes/logs it, retries iget, commits, reopens transaction, attaches dquots, locks the inode, and propagates zapped sick bits.
- `xrep_dinode_problems` schedules quotacheck after rebuilding a badly damaged dinode.

Main incore repair:
- `xrep_inode_blockcounts` recomputes data/attr fork extent and block counters.
- `xrep_inode_ids` resets invalid uid/gid/project IDs and forces quota checks as needed.
- `xrep_inode_timestamps` clamps timestamps to valid nanosecond ranges and filesystem granularity.
- `xrep_inode_flags` clears invalid or contradictory inode flags.
- `xrep_inode_dir_size` repairs directory size from shortform bytes or last block extent.
- `xrep_inode_pptr` ensures an attr fork exists when parent pointers are enabled and the inode should have one.
- `xrep_inode_extsize` and `xrep_inode_cowextsize` clear invalid realtime-aligned hints.
- `xrep_inode_problems` applies incore fixes and logs the inode core.
- `xrep_inode_unlinked` reconciles link count with the incore unlinked list.
- `xrep_inode` orchestrates raw repair if needed, incore repair for corrupt or cross-corrupt results, reflink flag clearing, unlinked-list repair, and deferred-op finishing.

Important policy:
- Unknown or invalid mode is made a root-readable regular file unless directory entries reveal a better type.
- Zapping attr forks removes access bits and resets ownership because ACLs may have been lost.
- Data/attr forks are zapped only enough to make higher-level bmap, directory, symlink, or xattr repair possible later.
- If directory scanning for mode recovery hits temporary busy state, repair returns without continuing destructive changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/inode_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/iscan.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/iscan.c

Implements live filesystem inode scanning for scrub/repair code that must visit all allocated inodes while racing safely with inode creation, deletion, and metadata updates.

Main mechanisms:
- The scan starts at a rotating AG-derived inode number to distribute load.
- `xchk_iscan_find_next` walks the inobt under AGI lock to find the next allocated inode, optionally masking `skip_ino`.
- `xchk_iscan_move_cursor` advances both the next-scan cursor and visited cursor over sparse inode-number gaps while AGI prevents allocation/free races.
- `xchk_iscan_advance` moves across AGs until it finds allocated inodes or wraps to the start.
- `xchk_iscan_iget` grabs up to one inode chunk of consecutive allocated inodes, using noretry/dontcache flags, retrying around inodegc races, and recording skipped unallocated inodes in a mask.
- `xchk_iscan_iter_batch` and `xchk_iscan_iter` expose one inode at a time to callers while internally batching igets.
- `xchk_iscan_iter_finish`, `xchk_iscan_finish`, `xchk_iscan_finish_early`, and `xchk_iscan_teardown` release cached inodes and mark scan completion.
- `xchk_iscan_mark_visited` advances the visited cursor after the caller has safely scanned an inode.
- `xchk_iscan_want_live_update` tells hook code whether an inode has already been scanned, was skipped in a batch, or falls in the wrapped visited range, and therefore needs live update replay.

Important correctness model:
- Advancing the cursor happens while AGI is locked so inode allocation/free cannot invalidate the observed range.
- Callers must hold sufficient inode locks before marking visited.
- Live-update hook code uses the visited cursor to update scan-derived indexes for inodes modified after being scanned.
- Trylock-AGI mode supports callers that already hold locks where blocking on AGI could deadlock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/iscan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/iscan.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/iscan.h

Defines the live inode scan state and public API.

Key fields in `struct xchk_iscan`:
- `scan_start_ino`, `cursor_ino`, and `__visited_ino` define scan progress and wraparound.
- `skip_ino` excludes a specific inode from scanning.
- `__opstate` stores abort and trylock-AGI flags.
- `iget_timeout`, `iget_retry_delay`, and `__iget_deadline` control inode acquisition retries.
- `__batch_ino`, `__skipped_inomask`, and `__inodes[]` support chunk-sized batching and live updates for skipped inodes.

Public API:
- Start/finish/teardown: `xchk_iscan_start`, `xchk_iscan_finish_early`, `xchk_iscan_teardown`.
- Iteration: `xchk_iscan_iter`, `xchk_iscan_iter_finish`.
- Progress/update helpers: `xchk_iscan_mark_visited`, `xchk_iscan_want_live_update`.
- Inline state helpers: abort and trylock-AGI accessors.

This header is central to scrub tasks that build replacement metadata while the filesystem remains live.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/iscan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/listxattr.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/listxattr.c

Provides a low-level xattr iterator for scrub code. It walks every extended attribute entry without validation restarts and detects malformed attr dabtrees, including loops.

Main functions:
- `xchk_xattr_walk_sf` iterates shortform xattr entries from the incore attr fork.
- `xchk_xattr_walk_leaf_entries` iterates entries in a leaf block, passing local values directly and remote values as `NULL` plus length.
- `xchk_xattr_walk_leaf` reads and walks the single leaf-format attr block.
- `xchk_xattr_find_leftmost_leaf` descends node-format attr trees from block zero to the leftmost leaf, checking magic, headers, levels, and repeated blocks with a dablock bitmap.
- `xchk_xattr_walk_node` walks the leaf sibling chain in node-format xattrs, detects loops, optionally calls a per-leaf callback between leaves, and walks entries in each leaf.
- `xchk_xattr_walk` selects shortform, leaf, or node traversal after requiring the caller to hold ILOCK and loading attr fork extents when needed.

Important behavior:
- Returns `-EFSCORRUPTED` for malformed tree shape or loops.
- Does not perform cursor restarts; callers must already hold appropriate locks.
- Handles local and remote attribute entries uniformly through callback metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/listxattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/listxattr.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/listxattr.h

Declares callback types and the xattr walker:
- `xchk_xattr_fn` receives each attr entry’s flags, name, optional local value pointer, value length, and caller private data.
- `xchk_xattrleaf_fn` optionally runs between node-format leaf blocks.
- `xchk_xattr_walk` walks all xattrs for a locked inode.

The API is designed for scrub users that need raw enumeration of existing xattr records with corruption reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/listxattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/metapath.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/metapath.c

Scrubs and repairs metadata-directory paths. On metadir filesystems, key metadata files are reachable through paths under the metadata directory tree; this scrubber verifies that the expected directory entry points to the expected incore metadata inode.

Setup:
- `struct xchk_metapath` tracks scrub context, expected name, parent directory, child inode, locks, reservations, parent-pointer state, and scratch lookup args.
- `xchk_setup_metapath_scan` installs the target metadata inode, allocates state, stores parent/path, and builds an `xfs_name`.
- RT helpers set up `/rtgroups` and rtgroup metadata inode paths when realtime is enabled.
- Quota helpers set up `/quota` and per-quota inode paths when quota support is enabled.
- `xchk_setup_metapath` validates metadir support, rejects generation-based requests, handles probe, and dispatches by `sm_ino` metapath selector.

Scrub:
- `xchk_metapath_ilock_both` locks parent and child safely, retrying child lock with termination checks.
- `xchk_metapath` handles probe, requires a parent, allocates an empty transaction, locks both inodes, looks up the expected dirent in the parent, and marks corruption if missing or pointing to the wrong inode.

Repair, under online repair:
- `xrep_metapath_link` creates the expected dirent and parent pointer if enabled.
- `xrep_metapath_unlink` removes an incorrect dirent and optional parent pointer from the alleged child.
- `xrep_metapath_try_link` attempts to create the correct link, reporting the wrong child if a conflicting dirent exists.
- `xrep_metapath_try_unlink` removes the wrong child link, handling bogus/missing child inodes and races where the dirent changed.
- `xrep_metapath` ensures the child has an attr fork for parent pointers, computes link/unlink reservations, and loops link/unlink attempts until the path is correct or an error occurs.

Important invariants:
- Repairs run after other repairs because they create transactions and take ILOCKs.
- The parent directory itself might be corrupt, so locking is cautious.
- Parent pointers are maintained when the filesystem supports them.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/metapath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/newbt.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/newbt.c

Provides shared infrastructure for staging and bulk-loading replacement btrees during online repair. It reserves blocks, feeds them to btree bulk loaders, tracks unused reservation space, and commits or cancels reservations safely.

Main functions:
- `xrep_newbt_estimate_slack` chooses btree bulk-load slack, tightening trees when the AG or filesystem has less than about 10 percent free space, unless debug tunables override defaults.
- `xrep_newbt_init_ag` initializes new per-AG btree staging state with owner info, allocation hint, reservation type, reservation list, and bulk-load limits.
- `xrep_newbt_init_inode` initializes an inode-fork fake root for rebuilding file btrees.
- `xrep_newbt_init_metadir_inode` initializes metadata inode btree rebuild state using regular block allocation semantics until commit.
- `xrep_newbt_init_bare` initializes a minimal staging object for callers managing reservations manually.
- `xrep_newbt_add_blocks` creates a reservation record and, for transaction-backed allocations, schedules autoreap so uncommitted blocks can be freed.
- `xrep_newbt_add_extent` adds caller-supplied space to the reservation pool.
- `xrep_newbt_alloc_ag_blocks` and `xrep_newbt_alloc_file_blocks` allocate per-AG or file-based btree blocks, validate allocation hints, add reservations, and finish deferred ops as they go.
- `xrep_newbt_alloc_blocks` chooses AG or file allocation based on whether `sc->ip` is set.
- `xrep_newbt_free_extent` handles commit/cancel semantics for each reservation, freeing unused ranges with EFIs and autoreap handling.
- `xrep_newbt_free`, `xrep_newbt_commit`, and `xrep_newbt_cancel` clean reservation state after successful btree commit or aborted repair.
- `xrep_newbt_claim_block` hands one reserved block to the btree bulk loader, advances reservation usage, writes the correct short/long btree pointer, and relogs deferred frees.
- `xrep_newbt_unused_blocks` totals unconsumed reserved blocks.

Important behavior:
- Autoreap protects against block leaks if repair fails before commit.
- Unused committed reservation space is freed through deferred extent frees.
- The code periodically finishes deferred frees to avoid overlarge truncate-style EFI reservations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/newbt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/newbt.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/newbt.h

Defines new-btree staging structures and public helpers.

Structures:
- `struct xrep_newbt_resv` records one reserved extent: list link, per-AG reference, autoreap state, AG block start, length, and used block count.
- `struct xrep_newbt` records scrub context, optional custom allocator, reservation list, fake btree root, owner info, bulk-load geometry, allocation hint, and reservation type.

Public API:
- Initialization: `xrep_newbt_init_bare`, `xrep_newbt_init_ag`, `xrep_newbt_init_inode`, `xrep_newbt_init_metadir_inode`.
- Space management: `xrep_newbt_alloc_blocks`, `xrep_newbt_add_extent`, `xrep_newbt_cancel`, `xrep_newbt_commit`.
- Bulk-loader integration: `xrep_newbt_claim_block`.
- Accounting: `xrep_newbt_unused_blocks`.

This header is used by repair code that rebuilds btrees with staged fake roots before atomically installing them.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/newbt.h -->