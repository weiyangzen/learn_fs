# Group Research: XFS online scrub AG headers, allocation, attributes, bitmaps, and bmaps

Scope: `Docs/research_subset_a.md`

This grouped report covers the requested files under `sources/os/linux/linux/fs/xfs/scrub/`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agheader.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/agheader.c

This file implements online scrub checks for XFS allocation group headers: secondary superblocks, AGF, AGFL, and AGI. It is read-only validation code, with setup through `xchk_setup_agheader` and primary entry points `xchk_superblock`, `xchk_agf`, `xchk_agfl`, and `xchk_agi`.

The superblock scrubber intentionally skips AG 0 because mount-time validation already accepted the primary superblock. For secondary superblocks it reads the backup, normalizes verifier-style geometry failures into corruption, and compares fields against the mounted primary superblock. Fields fixed at mkfs time are treated as corruption if mismatched, whereas fields that can legitimately drift or are not always propagated to backups are marked for preening. It handles modern feature-dependent structure size checks, including CRC, metauuid, metadir, and zoned fields, and requires all unused trailing bytes to be zero. `xchk_superblock_xref` then cross-references the superblock block against free-space, inode, rmap, shared, and CoW-staging metadata.

The AGF scrub path validates AG length, allocation btree roots and levels, rmap/refcount roots when enabled, AGFL ring counters, and in-core perag counters. It cross-checks `agf_freeblks`, `agf_longest`, btree block counts, rmap block counts, and refcount block counts against live btree traversals. The AGFL path reads and rechecks the AGFL, verifies every entry is a valid AG block, confirms entry count consistency, cross-references each listed block as AG-owned metadata, and sorts entries to detect duplicates.

The AGI scrub path validates AG length, inobt/finobt roots and levels, inode counters, `newino` and `dirino`, unlinked bucket head validity, padding, and in-core inode counters. `xchk_iunlink` walks in-memory unlinked lists while the AGI is held to verify bucket membership, lookup success, and inode unlinked-list state.

Important invariants are that header blocks must be used filesystem metadata, not inode chunks, not shared, not CoW staging, and owned by the expected rmap owner. Cross-reference checks generally stop after primary corruption is already flagged to avoid noisy or unsafe follow-on validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agheader.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agheader_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/agheader_repair.c

This file implements online repair for the same AG header objects checked by `agheader.c`: secondary superblocks, AGF, AGFL, and AGI. Repair is deliberately conservative and generally requires rmapbt support for reconstructing allocation group state from reverse mappings.

`xrep_superblock` repairs only secondary superblocks. It refuses AG 0, obtains the secondary superblock buffer, zeroes it, copies the mounted primary superblock into it, clears secondary-ignored NEEDSREPAIR and log-incompat feature bits, sets the buffer type, and logs the full block.

The AGF repair flow uses `xrep_find_ag_btree_roots` and rmap ownership to rediscover bnobt, cntbt, rmapbt, and refcountbt roots. It validates candidate roots and checks that the rediscovered rmapbt root matches the old AGF, because the rmapbt is the trusted source used to rebuild the header. `xrep_agf_init_header` rewrites the AGF fixed fields while preserving AGFL ring state, marks perag AGF state stale, installs roots, recalculates free-block, longest-free, btree-block, rmap-block, and refcount-block counters by walking the rebuilt btrees, logs the result, reinitializes perag counters, and rolls the AG transaction.

The AGFL repair path identifies AGFL blocks by collecting OWN_AG rmaps and subtracting current bnobt, cntbt, rmapbt, and cross-linked metadata blocks. It caps the rebuilt AGFL to the AGFL array size, rewrites the AGFL header and block array, updates AGF ring counters, rolls the transaction, and reaps overflow blocks back to free space.

The AGI repair path finds inobt and optional finobt roots through rmap data, rewrites AGI fixed fields, recalculates inode and btree block counters, and rebuilds unlinked inode buckets. The unlinked repair logic combines existing on-disk bucket walking, incore inode radix-tree scanning, opportunistic on-disk inode reloads, bitmaps of unlinked aginos, and staged `xfarray` next/prev pointer maps. It then logs inode unlinked pointer fixes and writes rebuilt bucket heads into the AGI.

Key risks handled here include chicken-and-egg dependencies between corrupt headers and btree discovery, stale perag state, old buffer verifier races after btree height changes, and preserving/reloading unlinked inode state without losing inodes that require inactivation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agheader_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agino_bitmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/agino_bitmap.h

This header provides a small type-safe wrapper around `struct xbitmap32` for per-allocation-group inode numbers (`xfs_agino_t`). The wrapper type is `struct xagino_bitmap`, which contains one `xbitmap32` named `aginobitmap`.

The API consists of inline helpers to initialize, destroy, set, clear, test, and walk bitmap ranges: `xagino_bitmap_init`, `xagino_bitmap_destroy`, `xagino_bitmap_clear`, `xagino_bitmap_set`, `xagino_bitmap_test`, and `xagino_bitmap_walk`. Each helper forwards directly to the corresponding `xbitmap32` routine while preserving the semantic type of the start value as `xfs_agino_t`.

The main role in this group is supporting AGI unlinked-list repair in `agheader_repair.c`, where the repair code needs compact range tracking for per-AG inode numbers that are known or suspected to be unlinked. Keeping this as a wrapper prevents accidental mixing of AG block numbers, filesystem block numbers, and AG inode numbers while reusing the interval-tree backed 32-bit bitmap implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agino_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/alloc.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/alloc.c

This file implements online scrub for XFS free-space btrees: bnobt and cntbt. `xchk_setup_ag_allocbt` prepares AG btree scrub state, optionally enables intent draining, and, when repair is available, performs allocation-btree repair setup.

The central record validator is `xchk_allocbt_rec`. It decodes an on-disk allocation btree record into `xfs_alloc_rec_incore`, validates the free-space extent with `xfs_alloc_check_irec`, detects adjacent mergeable free records that should have been coalesced, and cross-references the record against other metadata. Cross-reference checks require a matching record in the peer free-space btree: bnobt records must appear in cntbt and cntbt records must appear in bnobt with the same start block and length.

Additional xrefs assert that free extents are not inode chunks, have no rmap owner, are not shared blocks, and are not CoW staging blocks. The common helper `xchk_xref_is_used_space` is exported for other scrubbers in this group; it queries bnobt for records overlapping a supposedly allocated range and flags corruption if the range appears free.

Important invariants are that free-space records are physically valid, non-overlapping, non-adjacent when they could merge, mutually represented in both allocation btrees, and not claimed by inode, rmap, refcount, or CoW metadata. The code avoids xref work when the scrub item already carries primary corruption or xref skipping is requested.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/alloc_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/alloc_repair.c

This file repairs the XFS free-space btrees by reconstructing both bnobt and cntbt from reverse mapping data. It treats the rmapbt as authoritative for used space, derives free space from gaps in rmap records, stages replacement btrees, commits them into the AGF, and reaps old btree blocks.

`xrep_setup_ag_allocbt` flushes the AG busy extent list because repair cannot safely put the same extents on the busy list twice. The main repair context `struct xrep_abt` tracks OWN_AG blocks, blocks known not to be old allocbt blocks, staged new btrees, free-space records in an `xfarray`, free block totals, and longest extent length.

Collection is performed by `xrep_abt_find_freespace`. It walks all rmap records, records OWN_AG extents, records the current rmapbt path, detects gaps between physical mappings as free space, adds the trailing gap to EOAG, scans AGFL blocks, and subtracts current rmapbt/AGFL metadata from OWN_AG to identify possible old bnobt/cntbt blocks. Candidate free extents are checked against inode chunks and refcount/shared/CoW state before being stashed.

Rebuild uses an iterative reservation algorithm. Free extents are sorted by length, btree geometry is estimated, blocks are reserved from the discovered free records, and the process repeats until sufficient space exists for both new trees. The code then bulk-loads cntbt by length order and bnobt by block-number order, installs staged roots in the AGF, resets AGF free-space counters, updates alternate perag btree heights to avoid verifier races with old blocks, disposes of unused reservations, rolls the transaction, and reaps old allocation-btree blocks.

`xrep_revalidate_allocbt` reruns scrub of both bnobt and cntbt after repair, temporarily changing scrub type so tree-to-tree xrefs run in both directions. The file depends on rmapbt; without it, online repair is unsupported.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/alloc_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/attr.c

This file scrubs extended attribute metadata for an inode. It validates shortform attributes, attr leaf blocks, dabtree indexing, remote value retrieval, namespace flags, and parent pointer attribute values.

`xchk_setup_xattr_buf` manages reusable scrub scratch storage in `struct xchk_xattr_buf`: bitmaps for used/free bytes in attr blocks, an optional name buffer for repair, and a dynamically sized value buffer. `xchk_setup_xattr` invokes repair setup when possible, preallocates maximum buffers during try-harder retries, and then prepares inode content scrub locking.

For semantic validation, `xchk_xattr_actor` is called by xattr walking. It rejects unknown on-disk flags, marks incomplete attributes for preening, checks names with `xfs_attr_namecheck`, validates parent pointer values, allocates a buffer large enough for the value, and calls `xfs_attr_get_ilocked` after setting the hash to ensure the attribute can be found through normal lookup paths. Value length mismatches or lookup failures are flagged as corruption.

For physical layout validation, `xchk_xattr_set_map` tracks byte occupancy within shortform or leaf blocks and detects overlaps/out-of-range regions. `xchk_xattr_check_sf` walks shortform entries, validates entry bounds and legal flags, and marks header, entry, name, and value regions as used. Leaf-block checking validates padding, leaf header bounds, empty leaf cases, entry array placement, monotonic hash order, name/value storage bounds, local versus remote entry rules, freemap consistency, freemap/usedmap disjointness, and `usedbytes`.

`xchk_xattr_rec` ties the generic dabtree scrubber to attr-specific record validation by checking hash ordering and recomputing hashes for local and remote entries. Parent pointer attributes are not allowed to be remote in this logic. After physical checks pass, the scrubber performs a name/hash lookup pass over all attributes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/attr.h

This header declares shared scratch storage and helpers for extended attribute scrub and repair. `struct xchk_xattr_buf` contains a used-space bitmap, a free-space bitmap, a salvaged-name buffer, and a value buffer with its current allocation size.

The declared functions are `xchk_xattr_set_map`, which marks byte ranges in a bitmap while detecting overlaps and out-of-bounds regions, and `xchk_setup_xattr_buf`, which allocates or resizes the reusable scrub/repair buffers. These declarations are used by both `attr.c` and `attr_repair.c` so that repair can reuse the same occupancy-map and value-buffer logic used by scrub validation.

The header is intentionally small and has no policy logic; it defines the common data contract for xattr metadata checking and salvage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/attr_repair.c

This file repairs extended attribute metadata by salvaging valid attributes, replaying them into a temporary file, and atomically exchanging the rebuilt attr fork into the file being repaired. It supports parent pointer filesystems by capturing live directory updates during repair and replaying those changes into the temporary file before commit.

The repair context `struct xrep_xattr` tracks the tempfile exchange state, staged xattr keys in an `xfarray`, names/values in an `xfblob`, parent pointer update arrays and blobs, a directory update hook, scratch parent pointer arguments, and locking for live update capture. `xrep_setup_xattr` enables directory-entry update gating when parent pointers exist and creates a temporary regular file for the rebuild.

Salvage filters reject incomplete, nameless, oversized, invalid-name, invalid-value, and invalid-parent-pointer attributes. Shortform, local leaf, and remote leaf attributes have separate salvage paths. Remote values are recovered by finding suitable buffers, checking attr leaf structure where possible, reading remote values through XFS attr helpers, and ignoring corrupted remote values rather than failing the whole repair. Staged names and values are periodically flushed into the tempfile when memory use exceeds eight pages.

The non-inline scanner walks attr fork extents, probes the buffer cache and disk for possible attr leaf blocks, salvages entries from structurally plausible leaves, and carefully stales single-block buffers that might alias multiblock remote-value buffers. If parent pointer updates occur during a flush, `xrep_xattr_full_reset` clears the tempfile attr fork and restarts salvage without further periodic flushing to regain a consistent base.

Rebuild completion either zaps the repaired file's attr fork if no attributes were salvaged, or finalizes the tempfile by replaying queued parent pointer updates, preparing both attr forks for exchange, and using `xrep_tempexch_contents` to swap mappings. Local/local forks can be copied directly if the rebuilt shortform data fits. After exchange, the old attr fork now attached to the tempfile is reaped and cached ACLs are invalidated.

The top-level `xrep_xattr` requires both rmapbt, for reaping old attr blocks, and exchange-range support, for atomic replacement. Its major hazards are live parent pointer concurrency, buffer aliasing around remote attrs, memory growth from large attr sets, and preserving valid attrs while discarding corrupt entries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr_repair.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/attr_repair.h

This header exposes a narrow repair interface for extended attribute fork operations. It forward-declares `struct xrep_tempexch` and declares `xrep_xattr_swap`, `xrep_xattr_reset_fork`, and `xrep_xattr_reset_tempfile_fork`.

`xrep_xattr_swap` commits rebuilt tempfile attribute contents into the inode being repaired, either by direct local fork copy or by preparing both forks for an atomic mapping exchange. The reset helpers reap and reinitialize attr forks for the target inode or tempfile. These functions are used by xattr repair and by adjacent repair code that needs to clear corrupt attr fork state safely.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/attr_repair.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bitmap.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/bitmap.c

This file implements interval-tree backed sparse bitmaps for 64-bit and 32-bit integer spaces. The scrub/repair subsystem uses these bitmaps to track extents of filesystem blocks, AG blocks, and AG inode numbers without allocating dense bit arrays for large address spaces.

Both implementations use Linux interval tree generation macros over private node types. Each node records a start and last bit, plus the interval-tree subtree-last field. The public operations are mirrored for `xbitmap64` and `xbitmap32`: initialize, destroy, set, clear, subtract (`disunion`), count set bits (`hweight`), walk set ranges, test whether a range begins set or clear and for how long, and test emptiness. The 32-bit variant also counts the number of set regions.

`set` first clears the target range to eliminate overlapping nodes, then merges with left-adjacent and/or right-adjacent intervals when possible, otherwise allocates a new interval node. `clear` handles the four overlap cases: clearing the middle of a larger interval, trimming the left side, trimming the right side, or removing a fully covered interval. Splitting a node allocates a new right-side node, so memory allocation failure can be returned from clear/set operations.

`disunion` implements the repair pattern `bitmap &= ~sub` by walking every interval in `sub` and clearing it from `bitmap`. Many repair algorithms in this group use that to subtract still-live metadata from all blocks with a shared rmap owner, leaving likely stale blocks to reap.

Callers must not mutate a bitmap while walking it. Walk callbacks can return any nonzero value to stop iteration; `-ECANCELED` is documented as a caller-owned sentinel because the iterator itself does not generate it.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bitmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/bitmap.h

This header declares the sparse bitmap API implemented in `bitmap.c`. It defines `struct xbitmap64` and `struct xbitmap32`, each wrapping an `rb_root_cached`, and declares the complete operation set for both width variants.

For both 64-bit and 32-bit bitmaps the API includes `init`, `destroy`, `clear`, `set`, `disunion`, `hweight`, `walk`, `empty`, and `test`. The walk callback types are documented to return zero to continue and nonzero to stop, with `-ECANCELED` available as a caller-defined early-stop value. `xbitmap32_count_set_regions` is additionally exposed for callers that need extent-count rather than bit-count information.

This API is the generic base for typed wrappers such as AG block, filesystem block, and AG inode bitmaps. Its callers in scrub repair rely on sparse extent operations, especially subtraction and walking, to identify old metadata blocks and to replay or reap ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bmap.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/bmap.c

This file scrubs inode fork block mappings for data, attr, and CoW forks. It validates fork format, bmbt structure, incore extent records, physical target ranges, logical ordering, and cross-references against rmap, free-space, inode, refcount/shared, CoW staging, and realtime metadata.

`xchk_setup_inode_bmap` obtains and locks the inode, drains intents when needed, serializes with IO and mmap activity for regular data/CoW fork checks, breaks layouts for repair, flushes dirty page-cache data, optionally invalidates page cache before repair, allocates a scrub transaction, attaches quotas, and takes `ILOCK_EXCL`.

The core scrub context `struct xchk_bmap_info` records the fork, previous mapping, incore extent cursor, realtime status, shared/reflink status, and whether the incore extent tree was already loaded. Btree-format forks are scrubbed by `xchk_bmap_btree`, which loads extents, runs the generic btree checker, verifies btree block owners for CRC filesystems, and compares btree records to the incore extent tree when appropriate.

The incore mapping pass coalesces adjacent logical and physical records where safe, including a guard against merging across realtime group boundaries. It detects holes in extent arrays, excessive record lengths, out-of-order mappings, invalid file offsets, invalid data or realtime block ranges, unwritten attr extents, and directory/attr offsets that cannot fit in `xfs_dablk_t`. Delalloc reservations are checked separately for file-range validity and max extent length.

Datadev and realtime xrefs verify that mapped space is allocated, not an inode chunk, has a matching rmap owner/offset/flags, is not incorrectly shared, and has correct CoW staging state. CoW fork rmaps are checked with owner `XFS_RMAP_OWN_COW` and no file offsets. For suspicious empty data or attr forks, the scrubber can scan all AG or realtime rmap btrees to find rmaps for the inode that lack matching bmap records, which detects fork-zap damage.

Entry points are `xchk_bmap_data`, `xchk_bmap_attr`, and `xchk_bmap_cow`. Data and attr variants also clear the corresponding zapped-health state when the fork validates cleanly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bmap_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/bmap_repair.c

This file repairs inode data and attr fork block mappings by reconstructing the fork from reverse mapping records. It gathers all rmaps owned by the inode and relevant fork, stages a new extent list or bmap btree, swaps the staged fork into the inode, updates counters and quotas, and reaps old bmbt blocks.

`struct xrep_bmap` tracks old bmbt blocks in an `xfsb_bitmap`, a staged `xrep_newbt`, recovered bmap records in an `xfarray`, total file-owned blocks, old bmbt block count, real mapping count, target fork, reflink scan state, and whether unwritten extents are permitted. Data fork repair permits unwritten extents; attr fork repair does not.

Rmap scanning walks realtime groups when applicable and all AGs on the data device. For each matching inode owner, the code validates that records are physically within the group, logically valid, not free space, not inode chunks, and not contradictory in flags. It records all file-owned blocks for later `i_nblocks` reconstruction, records old bmbt blocks separately, filters to the requested fork, and converts data records into one or more bmbt records capped at `XFS_MAX_BMBT_EXTLEN`. Existing delalloc reservations from the incore extent tree are preserved for eligible forks.

For reflink filesystems, repair preserves an existing reflink inode flag and can discover shared data extents via refcount btree lookup to set `XFS_DIFLAG2_REFLINK` when rebuilding a regular file that was missing the flag. Recovered records are sorted by file offset and checked for overlap.

Rebuild chooses extents format when the real mapping count fits the fork, otherwise bulk-loads a new bmap btree. It initializes a staged inode fork, reserves blocks for btree format with quota override, loads real mappings into the btree and all mappings including delalloc into the incore extent tree, commits the staged fork, recalculates `i_nblocks` by combining rmap-discovered file blocks with the delta in bmbt block count, adjusts quota block counts, commits newbt reservations, rolls the transaction, and reaps old bmbt blocks with the inode bmbt owner info.

`xrep_bmap_check_inputs` requires rmapbt support, ignores nonexistent or local/device/UUID/meta-btree forks, and validates that only files, symlinks, and directories receive data fork repair. Entry points are `xrep_bmap_data` and `xrep_bmap_attr`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/bmap_repair.c -->