# Group Research: group_1888_xfsprogs_sources_local_fs_xfsprogs_repair_rmap_c_sources_local_fs_x_6bd1a54bf0a9

Scope confirmed against `Docs/research_subset_a.md`: `sources/local-fs/xfsprogs` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rmap.c -->
# File Research: sources/local-fs/xfsprogs/repair/rmap.c

Implements xfs_repair reverse-mapping and refcount reconstruction support. It owns per-AG and per-realtime-group in-memory rmap collection, verification of existing rmap/refcount btrees, reflink flag reconciliation, and size estimation for phase-5 rebuilds.

Key structures:
- `struct xfs_ag_rmap`: per AG/rtgroup anchor for an in-memory `xfbtree`, xfile buffer target, AG-btree rmap slab, refcount item slab, and AGFL count bookkeeping.
- Global arrays `ag_rmaps` and `rg_rmaps` hold per-AG and per-rtgroup state.
- `rmapbt_suspect` and internal `refcbt_suspect` suppress verification and force rebuild behavior after scanner-detected corruption.

Core flow:
- `rmaps_init` allocates per-AG and per-rtgroup tracking when rmap/refcount work is needed.
- `rmap_add_rec`, `rmap_add_bmbt_rec`, `rmap_add_fixed_ag_rec`, and `rmap_add_fixed_rtgroup_rec` collect observed file, bmbt, fixed metadata, inode chunk, log, and rt superblock ownership.
- `compute_refcounts` walks sorted rmap observations with an `rcbag` stack to emit shared refcount records wherever overlap depth changes.
- `rmaps_verify_btree` and `rtrmaps_verify_btree` compare observed rmaps with existing ondisk AG or rtgroup rmap btrees.
- `check_refcounts` and `check_rtrefcounts` compare computed refcount slabs with existing refcount btrees.
- `fix_inode_reflink_flags` updates inode reflink flags based on observed shared extents.
- `rmap_commit_agbtree_mappings` finishes inserting AG btree and AGFL ownership records into the rebuilt rmapbt after AGF/AGFL reconstruction.
- Estimators compute expected rmap/refcount btree block counts for AG and realtime trees.

Important behavior:
- File data rmaps, bmbt blocks, metadata owners, attr fork flags, unwritten flags, and realtime mappings are normalized into `xfs_rmap_irec`.
- Only written data fork extents from regular inodes are considered shareable for refcount generation.
- Reflink flag correction is deliberately quiet unless verbose, because clearing unnecessary reflink flags is an optimization.
- AGFL handling avoids double-recording `OWN_AG` blocks already represented by rebuilt AG btree mappings.
- Realtime rmap/refcount validation checks metadata btree inode format, metatype, and forbidden attr forks.

Dependencies:
- Uses `slab.c` for refcount and delayed AG btree records.
- Uses libxfs in-memory btrees, rmap/refcount helpers, bitmap helpers, `rcbag`, `rt.h`, and inode in-core repair state.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rmap.h -->
# File Research: sources/local-fs/xfsprogs/repair/rmap.h

Public interface for repair-time rmap/refcount collection, verification, and rebuild support.

Exports:
- Global state: `collect_rmaps`, `rmapbt_suspect`.
- Lifecycle: `rmap_needs_work`, `rmaps_init`, `rmaps_free`.
- Observation collection: `rmap_add_rec`, `rmap_add_bmbt_rec`, `rmap_add_fixed_ag_rec`, `rmap_add_fixed_rtgroup_rec`, `rmap_add_agbtree_mapping`, `rmap_commit_agbtree_mappings`.
- In-memory cursor access: `rmap_init_mem_cursor`, `rmap_get_mem_rec`.
- Verification and avoidance: `rmaps_verify_btree`, `rtrmaps_verify_btree`, `rmap_avoid_check`, `refcount_avoid_check`.
- Refcount generation/access: `compute_refcounts`, `refcount_record_count`, `init_refcount_cursor`, `check_refcounts`, `check_rtrefcounts`.
- Reflink flag repair: `record_inode_reflink_flag`, `fix_inode_reflink_flags`.
- Rebuild estimation/population: AG rmap/refcount and realtime rmap/refcount block estimators plus rtgroup btree population entry points.

This header is the bridge between phase scanners, inode repair, AG btree rebuild code, and realtime metadata rebuilders.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rt.c -->
# File Research: sources/local-fs/xfsprogs/repair/rt.c

Implements realtime bitmap/summary reconstruction, rt metadata inode discovery, rtgroup inode tracking, and realtime superblock checking.

Key data:
- `rtg_inodes[XFS_RTGI_MAX]`: bitmaps of discovered rt metadata inode numbers.
- `rtginodes_bad[]`: per-rt-metadata-type corruption flags.
- `struct rtg_computed`: computed realtime bitmap and summary buffers per rtgroup.
- `rt_computed`: array indexed by rtgroup.

Core flow:
- `generate_rtinfo` allocates per-rtgroup computed buffers and calls `generate_rtgroup_rtinfo`.
- `generate_rtgroup_rtinfo` walks realtime extent allocation state from repair block maps and produces bitmap words plus summary counts.
- `check_rtbitmap` and `check_rtsummary` compare computed data against existing rt metadata file contents.
- `fill_rtbitmap` and `fill_rtsummary` rewrite rt metadata file blocks from computed buffers.
- `discover_rtgroup_inodes` loads reachable rt metadata inodes before phase-3 inode clearing and records them in bitmaps.
- `unload_rtgroup_inodes` drops loaded rt metadata inodes before phase-6 rebuild.
- `mark_rtgroup_inodes_bad` releases a metadata type across all rtgroups and marks it for rebuild.
- `check_rtsb` reads the realtime superblock and rewrites it if invalid and modification is allowed.
- `rewrite_rtsb` updates the realtime superblock from the primary filesystem superblock.

Important behavior:
- Supports both old sb-rooted realtime bitmap/summary files and newer rtgroup metadata.
- Realtime bitmap word layout differs for rtgroups versus older filesystems; helpers abstract endian/layout writes.
- For rtgroups, metadata block owner headers are checked while validating rt files.
- Missing or unloadable sb-rooted rt files set `need_rbmino` or `need_rsumino` so later phases can recreate them.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rt.h -->
# File Research: sources/local-fs/xfsprogs/repair/rt.h

Header for realtime repair helpers.

Exports:
- Realtime bitmap/summary generation and validation: `generate_rtinfo`, `check_rtbitmap`, `check_rtsummary`, `fill_rtbitmap`, `fill_rtsummary`.
- Rtgroup metadata inode lifecycle: `discover_rtgroup_inodes`, `unload_rtgroup_inodes`, `init_rtgroup_inodes`, `free_rtgroup_inodes`.
- Metadata inode classification: `is_rtgroup_inode` plus inline wrappers for bitmap, summary, rmap, and refcount inode types.
- Corruption tracking: `mark_rtgroup_inodes_bad`, `rtgroup_inodes_were_bad`.
- Realtime superblock operations: `check_rtsb`, `rewrite_rtsb`.

The header is consumed by repair phases and rmap/refcount code that need to avoid or rebuild rtgroup metadata.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rt.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rtrefcount_repair.c -->
# File Research: sources/local-fs/xfsprogs/repair/rtrefcount_repair.c

Rebuilds the realtime refcount btree for a realtime group from computed repair-time refcount records.

Key structure:
- `struct xrep_rtrefc`: holds slab cursor, staged inode fork bulkload state, repair context, rtgroup, and estimated free-data-block budget.

Core flow:
- `populate_rtgroup_refcountbt` opens a transaction for the rtgroup refcount inode and calls `xrep_rtrefc_build_new_tree`.
- `xrep_rtrefc_build_new_tree` stages a new metadata btree fork, bulkloads records, commits the staged root, updates inode counters, commits bulkload accounting, and rolls the transaction.
- `xrep_rtrefc_btree_load` computes btree geometry from `refcount_record_count`, reserves transaction space, allocates file blocks, initializes a refcount slab cursor, and calls libxfs bulkload.
- `xrep_rtrefc_get_records` feeds `xfs_refcount_irec` records from the slab cursor into btree blocks.
- `xrep_rtrefc_claim_block` delegates new btree block ownership to the bulkload layer.
- `xrep_rtrefc_iroot_size` calculates staged in-core root size for rtrefcount format.

Important behavior:
- No work is done unless realtime reflink is enabled.
- The new fork is explicitly marked `XFS_DINODE_FMT_META_BTREE`.
- Quota updates are unnecessary for these metadata inodes.
- On error, staged bulkload state is canceled and the transaction is canceled by the caller.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rtrefcount_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rtrmap_repair.c -->
# File Research: sources/local-fs/xfsprogs/repair/rtrmap_repair.c

Rebuilds realtime reverse-mapping btrees for rtgroups from the in-memory rmap observations collected during earlier repair phases.

Key structure:
- `struct xrep_rtrmap`: holds an in-memory rmap btree cursor, staged new inode fork state, bulkload geometry, repair context, rtgroup, and estimated free block budget.

Core flow:
- `populate_rtgroup_rmapbt` creates a transaction for the rtgroup rmap inode and rebuilds the tree if realtime rmapbt is enabled.
- `xrep_rtrmap_build_new_tree` stages a metadata btree fork, bulkloads all observed rtrmap records, commits the staged tree, updates counters, commits bulkload state, and rolls the transaction.
- `xrep_rtrmap_btree_load` computes geometry from `rmap_record_count`, reserves transaction blocks, allocates file blocks, opens an in-memory rmap cursor, and invokes libxfs bulkload.
- `xrep_rtrmap_get_records` feeds records from `rmap_get_mem_rec`.
- `rtgroup_update_counters` recalculates used blocks for zoned filesystems and updates `i_used_blocks`.

Important behavior:
- On rebuild failure, this file calls `do_error`, because the rtgroup rmapbt is required for enabled rtrmap filesystems.
- Rebuilt rt rmap btree blocks are owned through the bulkload file-block allocator.
- Zoned filesystems receive special used-block counter recomputation from the realtime block map.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rtrmap_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/sb.c -->
# File Research: sources/local-fs/xfsprogs/repair/sb.c

Handles superblock validation, primary superblock recovery from secondaries, geometry voting, and primary superblock writes.

Core flow:
- `verify_sb` validates superblock magic, version, in-progress flag, sector size/logs, CRC, block size, filesystem geometry, inode geometry, log geometry, realtime geometry, inode alignment, inode percentage, stripe settings, directory block size, metadata directory padding, and rtgroup geometry.
- `find_secondary_sb` tries to locate a valid secondary superblock using current geometry, guessed default geometry, and finally brute-force scanning.
- `__find_secondary_sb` scans the device in large buffers, checks candidate superblocks every basic block, and verifies them by calling `verify_set_primary_sb`.
- `verify_set_primary_sb` reads secondary superblocks, builds a geometry vote list, requires enough agreement, optionally force-accepts weak cases, and copies the best geometry into the primary candidate.
- `copy_sb` copies only fields that should be common between primary and secondary superblocks, preserving primary-only inode pointers and version bits.
- `write_primary_sb` writes a primary superblock buffer and recalculates CRC when needed.
- `get_sb` reads and validates a superblock at a specific offset.
- Geometry helpers build and compare `fs_geometry_t` records.

Important behavior:
- Two-AG and one-AG filesystems require `force_geometry` when geometry cannot be independently validated.
- Metadata-directory filesystems cause a warning that quota accounting/enforcement flags can be lost when recovering from a secondary.
- Realtime group validation checks rg count/extents, rextsize, maxes, required exchange feature, and computed rg block log.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/sb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/scan.c -->
# File Research: sources/local-fs/xfsprogs/repair/scan.c

Implements phase scanning of allocation groups, on-disk btrees, AG headers, block ownership maps, inode btrees, rmap/refcount btrees, realtime metadata btrees, and global counter validation.

Key structures:
- `struct aghdr_cnts`: per-AG manual counters for AGF/AGI and superblock validation.
- `struct rmap_priv`: scanner state for rmap btree high-key/last-record validation.
- `struct refc_priv`: scanner state for refcount btree validation.
- `struct ino_priv`: inode and free-inode btree scan accounting.

Core traversal:
- `salvage_buffer` reads buffers even after verifier failure, producing zeroed suspect buffers on EIO.
- `scan_sbtree` walks short-form AG btrees by AG block number.
- `scan_lbtree` walks long-form inode-hosted btrees by fsblock and handles dirty CRC/key repairs.
- `scan_bmapbt` validates inode bmap btrees, sibling links, owner/blkno/uuid, key ordering, extents, duplicate claims, and optionally records bmbt rmaps.

AG metadata scans:
- `scan_allocbt` validates bnobt/cntbt records, free-space ordering, block ownership states, and free-block counters.
- `scan_rmapbt` validates AG rmapbt records, ordering, owners, impossible field combinations, high keys, merge opportunities, and block-owner consistency.
- `scan_refcbt` validates AG refcountbt records, CoW/shared domains, counts, ordering, merge opportunities, and block claims.
- `scan_freelist` walks AGFL entries and marks them free.
- `validate_agf` drives bnobt/cntbt/rmapbt/refcountbt scans and compares counted fields against AGF values.
- `validate_agi` drives inobt/finobt scans, checks block counts, inode counts, free counts, and unlinked buckets.

Realtime metadata scans:
- `process_rtrmap_reclist` and `scan_rtrmapbt` validate realtime rmap records and inode-hosted rtrmap btrees.
- `process_rtrefc_reclist` and `scan_rtrefcbt` validate realtime refcount records and inode-hosted rtrefcount btrees.
- Suspect realtime rmap/refcount trees call the same avoid-check paths as AG trees.

Inode btree logic:
- `verify_single_ino_chunk_align` validates inode chunk alignment and agino range.
- `import_single_ino_chunk` imports certain records into in-core inode trees or uncertain records when suspect.
- `scan_single_ino_chunk` handles allocation inobt records and marks inode blocks.
- `scan_single_finobt_chunk` cross-checks finobt against inobt-derived in-core state.
- `scan_inobt` walks inobt/finobt blocks and records bad inode btree state if corruption is detected.

Top-level:
- `scan_ag` reads SB/AGF/AGI, repairs AG headers when allowed, scans all AG structures, writes corrected headers/CRCs, and updates progress.
- `scan_ags` runs AG scans through the workqueue, aggregates counters, and compares them to superblock summary counters.

Important behavior:
- Scanner is intentionally salvage-oriented: it keeps walking suspect trees until consecutive corruption makes traversal unsafe.
- Block map states distinguish unknown, free, inode, fs metadata, rmap-observed, refcount, CoW, metadata-file, duplicate, and in-use states.
- Rmap/refcount corruption sets avoid flags so later phases rebuild instead of trusting old btrees.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/scan.h -->
# File Research: sources/local-fs/xfsprogs/repair/scan.h

Header for scanner entry points and reusable inode-hosted btree scan callbacks.

Exports:
- `set_mp` to set the scanner mount context.
- `scan_lbtree` generic long-format btree traversal.
- `scan_bmapbt` inode block-map btree validator.
- `scan_ags` top-level AG scanner.
- `struct rmap_priv` and `struct refc_priv` scanner-private state used by realtime btree scanners and repair code.
- `process_rtrmap_reclist`, `scan_rtrmapbt`, `process_rtrefc_reclist`, and `scan_rtrefcbt` for validating realtime rmap/refcount records and btrees.

The header lets inode repair and realtime metadata code reuse scanner logic for inode-hosted metadata btrees.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/scan.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/slab.c -->
# File Research: sources/local-fs/xfsprogs/repair/slab.c

Implements a grow-only slab array with cursor iteration and optional sorted merge traversal.

Key structures:
- `struct xfs_slab_hdr`: one slab segment with item capacity, used count, and next pointer.
- `struct xfs_slab`: logical collection of increasingly sized slab segments.
- `struct xfs_slab_cursor`: per-slab cursors used to iterate either insertion order or sorted order across independently sorted slabs.

Core API:
- `init_slab` and `free_slab` create/destroy slab arrays.
- `slab_add` appends one fixed-size item, allocating larger segments as needed.
- `qsort_slab` sorts each slab segment, parallelizing with workqueue if there are more than four slabs.
- `init_slab_cursor`, `peek_slab_cursor`, `advance_slab_cursor`, and `pop_slab_cursor` iterate data.
- `slab_count` returns total items.

Important behavior:
- No random access or deletion is supported.
- Pointers are not stable across sort operations.
- Sorted cursor traversal performs a k-way merge over individually sorted slab segments.
- Slabs start with at least 4096 items and cap individual slab allocation at 128 MiB.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/slab.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/slab.h -->
# File Research: sources/local-fs/xfsprogs/repair/slab.h

Public slab-array interface.

Defines opaque `struct xfs_slab` and `struct xfs_slab_cursor`, plus functions for:
- Allocation and free.
- Appending fixed-size items.
- Sorting with caller-provided comparator.
- Counting items.
- Cursor creation/destruction.
- Peeking, advancing, and popping items.

Used by rmap/refcount collection and bulkload rebuild paths to hold large temporary record streams.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/slab.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/strblobs.c -->
# File Research: sources/local-fs/xfsprogs/repair/strblobs.c

Implements deduplicated storage of length-explicit strings in an `xfblob`.

Key structures:
- `struct strblob_hashent`: hash table entry with blob cookie, string length, directory hash, and next pointer.
- `struct strblobs`: owns an `xfblob`, bucket count, and flexible bucket array.

Core API:
- `strblobs_init` creates an `xfblob` and hash table.
- `strblobs_destroy` frees hash entries and destroys blob storage.
- `strblobs_store` deduplicates by lookup, stores new strings in the blob, and records the cookie in the hash table.
- `strblobs_lookup` searches by hash/length and then loads candidates for byte comparison.
- `strblobs_load` retrieves string bytes by cookie.

Important behavior:
- Hash is an accelerator only; exact byte comparison prevents false dedupe.
- Returns positive errno-style values to callers while wrapping negative libxfs `xfblob` returns.
- Intended for repair subsystems that need compact temporary storage for repeated strings.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/strblobs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/strblobs.h -->
# File Research: sources/local-fs/xfsprogs/repair/strblobs.h

Header for deduplicated string blob storage.

Exports opaque `struct strblobs` and functions to:
- Initialize/destroy a string blob table.
- Store a string and receive an `xfblob_cookie`.
- Load a string by cookie.
- Lookup an existing string by bytes, length, and directory hash.

The interface is designed around explicit string lengths and xfs directory hash values.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/strblobs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/threads.c -->
# File Research: sources/local-fs/xfsprogs/repair/threads.c

Thin wrapper around libfrog workqueues plus signal masking for worker threads.

Functions:
- `thread_init` blocks `SIGHUP` and `SIGALRM` delivery to threads so progress/reporting signals remain controlled.
- `create_work_queue` wraps `workqueue_create` and converts errors into fatal repair errors.
- `queue_work` wraps `workqueue_add`.
- `destroy_work_queue` terminates and destroys a queue, fatal on termination errors.

Used by AG scanning, slab sorting, and other parallel repair operations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/threads.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/threads.h -->
# File Research: sources/local-fs/xfsprogs/repair/threads.h

Header for repair workqueue helpers.

Exports:
- `thread_init`
- `create_work_queue`
- `queue_work`
- `destroy_work_queue`

Includes `libfrog/workqueue.h`, exposing `struct workqueue` and `workqueue_func_t` to callers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/threads.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/versions.c -->
# File Research: sources/local-fs/xfsprogs/repair/versions.c

Parses and updates filesystem feature/version state from the superblock.

Global feature state:
- Attribute support, attr2, inode nlink, quotas, aligned inodes, superblock feature bits, extent flag bit.
- `fs_ino_alignment` stores inode chunk alignment in filesystem blocks.

Core functions:
- `parse_sb_version` validates supported version/features, rejects shared-version bit, detects unknown v5 features, initializes feature globals, registers quota inode numbers, and records inode alignment.
- `update_sb_version` updates the in-core superblock from feature globals, forces v2 inode nlink bit, adds attr/attr2/quota bits when needed, clears bogus quota flags, clears quota/alignment bits when unsupported, and refreshes mount feature flags.

Important behavior:
- V1 inode filesystems are warned as being converted to v2 inode behavior.
- Unsupported unknown compat/rocompat/incompat features cause repair to exit.
- Quota flags are sanitized even in no-modify mode because the in-core superblock will not be flushed.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/versions.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/versions.h -->
# File Research: sources/local-fs/xfsprogs/repair/versions.h

Header for repair feature/version globals and parsing/updating functions.

Exports:
- Feature globals such as `fs_attributes`, `fs_quotas`, `fs_aligned_inodes`, and `fs_has_extflgbit`.
- `fs_ino_alignment`.
- `update_sb_version` to modify superblock version/features from repair state.
- `parse_sb_version` to initialize repair globals from a mounted superblock.

Used by scanner and main repair setup to decide inode alignment checks and feature-specific repair behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/versions.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/xfs_repair.c -->
# File Research: sources/local-fs/xfsprogs/repair/xfs_repair.c

Main program driver for `xfs_repair`.

Major responsibilities:
- Parses command-line options and conversion/override suboptions.
- Initializes libxfs, mount state, caches, progress, block maps, inode maps, rmap state, and rtgroup inode tracking.
- Orchestrates phases 1 through 7.
- Protects modified CRC filesystems with `NEEDSREPAIR`.
- Handles final quota, secondary-super, realtime-super, log, flush, unmount, and exit-code behavior.

Important functions:
- `process_args` handles `-n`, `-L`, `-m`, `-r`, `-l`, `-o`, `-c`, `-P`, `-t`, `-e`, and debug/failure options.
- `err_string`, `do_error`, `do_abort`, `do_warn`, and `do_log` centralize diagnostics and fatal exits.
- `calc_mkfs` validates fixed-location inode expectations for root, metadata directory, realtime bitmap, and realtime summary.
- `guess_correct_sunit` tries to recover plausible stripe unit from secondary superblocks or root inode placement.
- `format_log_max_lsn` reformats the log if metadata LSNs are ahead of the current log cycle.
- `retain_primary_sb`, `force_needsrepair`, `repair_capture_writeback`, and `clear_needsrepair` manage crash protection during metadata writes.
- `bump_max_fds` raises fd limits for memfd/xfile-heavy repair workloads.

Main flow:
1. Parse arguments, initialize libxfs, and run phase 1 to obtain a valid superblock.
2. Mount libxfs repair context and initialize global geometry/state.
3. Tune parallelism and buffer cache size.
4. Initialize bmaps, inode trees, rmap structures, and rtgroup inode bitmaps.
5. Parse feature/version state.
6. Run phase 2, initialize prefetch, phase 3, rcbag cursor cache, phase 4, phase 5 unless no-modify, phase 6/7 unless inode btrees are too corrupted.
7. Emit quota warnings, stop progress, handle no-modify exit.
8. Update quota flags, secondary superblocks, realtime superblock, flush cache, reformat log if necessary, clear `NEEDSREPAIR`, unmount, and return status.

Important behavior:
- Automatic AG stride/threading increases parallelism on multidisk/high-AG filesystems.
- No-modify mode stops before phase 5 and exits nonzero if dirtiness was detected.
- `-e` returns code 4 if errors were corrected.
- `NEEDSREPAIR` is set before first non-super metadata write and cleared only after successful flush.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/xfs_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/zoned.c -->
# File Research: sources/local-fs/xfsprogs/repair/zoned.c

Validates zoned realtime devices against XFS rtgroup expectations.

Core flow:
- `check_zones` checks whether the realtime device is a block device and zoned via `BLKGETSIZE64` and `BLKGETZONESZ`.
- It verifies the device has enough zones for `sb_rgcount`.
- It reports zones in batches via `xfrog_report_zones`.
- For each zone, it checks consistent length, supported zone type, consistent capacity, and then calls `report_zones_cb`.
- `report_zones_cb` maps zone start sectors to realtime blocks/rtgroup, verifies the zone starts at rtgroup block zero, loads the rtgroup, warns if no rmap inode exists, and otherwise calls `libxfs_validate_blk_zone`.

Important behavior:
- Sequential-write-preferred and unknown zone types are fatal.
- Zone capacity must be consistent and not exceed zone size.
- Rtgroup rmap inode presence is important for full zone validation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/zoned.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/zoned.h -->
# File Research: sources/local-fs/xfsprogs/repair/zoned.h

Header for zoned realtime device validation.

Exports:
- `check_zones(struct xfs_mount *mp)`

Used by repair setup or realtime validation paths to ensure zoned block-device layout matches rtgroup metadata expectations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/zoned.h -->