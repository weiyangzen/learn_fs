# Group Research: group_1105_linux_stable_sources_os_linux_linux_stable_fs_xfs_scrub_agheader_c__631d428ef806

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agheader.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agheader.c

## Purpose
Implements online scrub checks for XFS allocation group header metadata: secondary superblocks, AGF, AGFL, and AGI. It validates header fields against mounted primary filesystem state, verifies per-AG counters and root pointers, and cross-references header-owned blocks with free space, inode, reverse-map, refcount, shared, and CoW staging metadata.

## Main Entry Points
- `xchk_setup_agheader`: enables intent drain if needed and sets up filesystem-wide scrub context.
- `xchk_superblock`: checks secondary superblocks only; AG 0 is trusted because mount already validated the primary superblock.
- `xchk_agf`: checks allocation group free-space header geometry, btree roots, levels, AGFL counters, and in-core perag counters.
- `xchk_agfl`: reads AGFL, walks listed free-list blocks, validates uniqueness and ownership.
- `xchk_agi`: checks inode allocation header geometry, inobt/finobt roots and levels, inode counters, inode pointer fields, unlinked buckets, and in-core perag counters.

## Key Behavior
`xchk_superblock` compares secondary superblock fields against `mp->m_sb`, separating hard corruption from preen-only drift. Immutable mkfs geometry and feature bits become corruption; mutable or repairable fields such as UUID propagation, quota inodes, labels, and some feature synchronization mismatches are marked preen. It also checks trailing bytes beyond the active superblock format are zero according to mounted features such as crc, metauuid, metadir, and zoned support.

`xchk_agf_xref` initializes AG btree cursors and confirms the AGF block is used, not an inode chunk, owned only by filesystem metadata, not shared, and not CoW staging. It recalculates `agf_freeblks` from bnobt, `agf_longest` from cntbt, btree block counters from bnobt/cntbt/rmapbt, and refcount block count from refcountbt.

`xchk_agfl` verifies the AGFL header block itself, then walks AGFL entries through `xfs_agfl_walk`. Valid entries must be valid AG blocks, owned as AG metadata, not shared or CoW staging, and unique after sorting. It detects AGF `agf_flcount` overflow beyond `xfs_agfl_size`.

`xchk_agi` validates AGI fields, checks inode btree roots/levels, validates inode count/freecount bounds, verifies newino/dirino/unlinked bucket aginos, and walks incore unlinked lists to catch bad bucket assignment or missing/unlinked-state mismatches.

## Dependencies and Interactions
Uses XFS scrub common helpers, allocation btrees, ialloc btrees, rmap/refcount cross-reference helpers, perag state, superblock feature helpers, and buffer recheck helpers. This file is the validation side paired with `agheader_repair.c`.

## Failure Handling
Verifier/read errors from secondary superblock reads are normalized to scrub corruption where appropriate. Cross-reference checks are skipped once primary corruption is already flagged. `-ECANCELED` is used internally by AGFL walking to stop after corruption without surfacing as a hard syscall error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agheader.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agheader_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agheader_repair.c

## Purpose
Repairs XFS AG header structures: secondary superblocks, AGF, AGFL, and AGI. It reconstructs headers from trusted primary superblock/perag state and from rmap-discovered btree roots, updates in-core perag state, and rebuilds AGI unlinked inode lists.

## Main Entry Points
- `xrep_superblock`: rewrites a secondary superblock from AG 0 mounted state.
- `xrep_agf`: reconstructs AGF fields and btree root metadata.
- `xrep_agfl`: reconstructs AGFL contents from rmap-derived AG metadata ownership.
- `xrep_agi`: reconstructs AGI fields, inobt/finobt roots, inode counters, and unlinked buckets.

## Key Behavior
`xrep_superblock` refuses AG 0 repair, obtains the secondary superblock buffer, zeroes it, copies mounted superblock state, clears secondary-ignored `NEEDSREPAIR` and log incompat bits, sets buffer type, and logs the entire block.

AGF repair requires rmapbt. It reads the possibly corrupt AGF directly, reads AGFL as a filter, uses `xrep_find_ag_btree_roots` to find bnobt/cntbt/rmapbt/refcountbt roots, insists the found rmapbt root matches the old AGF, reinitializes the AGF header, implants found roots, recalculates free-space counters and btree block counts by walking/counting the btrees, logs the buffer, and reinitializes perag AGF state.

AGFL repair also requires rmapbt. It collects all `OWN_AG` extents, removes blocks known to belong to bnobt/cntbt/rmapbt paths, removes crosslinked blocks, limits the new free list to `xfs_agfl_size`, rewrites the AGFL header and entries, updates AGF `flfirst/fllast/flcount`, rolls the AG transaction, and reaps overflow blocks back to free space.

AGI repair requires rmapbt. It finds inobt/finobt roots via rmap data, rebuilds AGI header fields, counts inodes and inobt/finobt blocks, and reconstructs `agi_unlinked[]`. The unlinked rebuild is extensive: it walks old ondisk buckets, reloads missing inodes when needed, scans incore inode cache, scans inobt records for uncached unlinked inodes, stages next/prev links in xfarrays, reinserts lost unlinked inodes, logs forward links, fixes incore back links, and finally writes rebuilt bucket heads.

## Dependencies and Interactions
Uses `scrub/bitmap.h`, `agb_bitmap.h`, `agino_bitmap.h`, `reap.h`, `xfile.h`, `xfarray.h`, rmapbt discovery helpers, perag init bits, and transaction rolling. It depends on rmapbt for all AGF/AGFL/AGI rebuilds except secondary superblocks.

## Failure Handling
Each repair has a last termination check before committing. AGF/AGI preserve old headers and revert on failures before final commit. AGFL uses bitmaps to avoid freeing crosslinked blocks. AGI teardown destroys unlinked-list staging arrays and bitmap state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agheader_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agino_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agino_bitmap.h

## Purpose
Provides a type-checked per-AG inode-number bitmap wrapper around `xbitmap32`.

## API
- `struct xagino_bitmap` contains one `struct xbitmap32`.
- `xagino_bitmap_init`
- `xagino_bitmap_destroy`
- `xagino_bitmap_clear`
- `xagino_bitmap_set`
- `xagino_bitmap_test`
- `xagino_bitmap_walk`

## Notes
The wrapper prevents accidental mixing of generic 32-bit bitmap units with `xfs_agino_t` values. It is used by AGI repair to track unlinked inodes while rebuilding unlinked bucket chains.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agino_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/alloc.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/alloc.c

## Purpose
Scrubs XFS free-space allocation btrees: bnobt and cntbt. It validates individual free-space records, detects mergeable adjacent records, and cross-references each record against the companion allocation btree and other AG metadata.

## Main Entry Points
- `xchk_setup_ag_allocbt`: prepares AG btree scrub and, if repair is possible, runs allocation btree repair setup.
- `xchk_allocbt`: selects bnobt or cntbt according to `sm_type` and invokes generic btree scrub.
- `xchk_xref_is_used_space`: shared xref helper that verifies a range is not present in free-space btrees.

## Key Behavior
Each allocation record is converted to incore format and checked with `xfs_alloc_check_irec`. `xchk_allocbt_mergeable` flags adjacent free-space records that should have been merged. `xchk_allocbt_xref_other` verifies a matching record exists in the other free-space btree. Additional xrefs ensure the free extent is not an inode chunk, has no owner in rmap, is not shared, and is not CoW staging.

## Dependencies and Interactions
Works with generic scrub btree traversal, allocation btree cursors stored in `sc->sa`, rmap/refcount xref helpers, and `alloc_repair.c` setup when repair is enabled.

## Failure Handling
Cross-reference checks are skipped after corruption is already detected or when the target cursor is unavailable. Btree cursor errors are processed through scrub xref helpers so a broken xref tree can be isolated from the tree under examination.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/alloc_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/alloc_repair.c

## Purpose
Repairs the AG free-space btrees, rebuilding both bnobt and cntbt from reverse-map information. The core model is: free space equals gaps in rmap coverage plus old `OWN_AG` allocation-btree blocks, minus rmapbt and AGFL blocks.

## Main Entry Points
- `xrep_setup_ag_allocbt`: flushes busy extents before scrub/repair.
- `xrep_allocbt`: full bnobt/cntbt rebuild for an AG.
- `xrep_revalidate_allocbt`: re-scrubs both btrees after rebuild by temporarily switching scrub type.

## Key Behavior
`xrep_abt_find_freespace` walks the rmapbt, records gaps as free extents, records `OWN_AG` blocks as possible old allocation btree blocks, records rmapbt path blocks, reads AGFL, and subtracts rmapbt/AGFL blocks from `OWN_AG` to identify old bnobt/cntbt blocks to reap.

Free extents are stored in an `xfarray`, sorted first by length for space reservation and cntbt construction, and later by block number for bnobt construction. `xrep_abt_reserve_space` iteratively reserves free extents for the new btrees until the computed btree geometry converges. Reserved blocks are tracked through `xrep_newbt`.

`xrep_abt_build_new_trees` creates staged bnobt and cntbt cursors, bulk-loads cntbt then bnobt, commits staged roots to the AGF, recalculates AGF counters, reinitializes perag AGF state, disposes unused reservations, rolls the AG transaction, and then `xrep_abt_remove_old_trees` reaps the old btree blocks.

## Dependencies and Interactions
Requires rmapbt. Uses free-space, rmap, ialloc, refcount, newbt, xfile/xfarray, AG block bitmap, and reaping helpers. It relies on AGF being readable enough to access rmapbt and AGFL during reconstruction.

## Failure Handling
Busy extents must be flushed before starting and must remain empty at repair time, otherwise repair returns `-EDEADLOCK`. All reserved newbt state is canceled on failure. Alternate perag btree heights are set during repair to keep write verifiers from rejecting old or new btree blocks while both can be in flight.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/alloc_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr.c

## Purpose
Scrubs extended attribute metadata for an inode. It checks shortform and leaf/block attribute structures, verifies space accounting inside attr blocks, validates names/flags/parent-pointer values, and confirms each attribute can be looked up by hash and value retrieval.

## Main Entry Points
- `xchk_setup_xattr`: prepares repair tempfile if needed, allocates larger buffers for retry, then sets up inode content scrub.
- `xchk_setup_xattr_buf`: allocates reusable used/free bitmaps, name buffer, and value buffer.
- `xchk_xattr`: top-level xattr scrub for shortform or dabtree-backed attributes.
- `xchk_xattr_set_map`: bitmap helper for detecting byte-range overlap/out-of-range within attr blocks or shortform data.

## Key Behavior
For every listed xattr, `xchk_xattr_actor` validates ondisk flags, incomplete state, name validity, parent-pointer value format, allocates enough scratch value space, and performs `xfs_attr_get_ilocked` after setting the attr hash. Lookup returning `-ENODATA` is treated as corruption.

Leaf block scrub tracks used bytes and free bytes with bitmaps. It validates header padding, empty leaf handling, header bounds, entry table placement, hash ordering, name/value entry bounds, duplicate byte usage, freemap conflicts, zero-length freemap preen cases, and `usedbytes`.

Shortform scrub checks entry iteration bounds, valid namespace-only flags, and non-overlapping ranges for entry headers, names, and values.

## Dependencies and Interactions
Uses XFS da btree scrub, attr leaf/shortform helpers, parent pointer validation, listxattr walking, and shared attr repair buffer state declared in `attr.h`.

## Failure Handling
Memory pressure while growing the attr value buffer returns `-EDEADLOCK` to trigger a retry with maximum buffer allocation. Structural corruption generally sets fork-block corruption and may stop further block processing. Incomplete attrs are preen candidates, not hard corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr.h

## Purpose
Declares temporary extended attribute scrub/repair buffer state and shared helper prototypes.

## Key Structures
`struct xchk_xattr_buf` stores:
- `usedmap`: byte bitmap for occupied space in shortform/leaf xattr storage.
- `freemap`: byte bitmap for advertised free space in leaf blocks.
- `name`: salvage/reinsert name scratch buffer.
- `value` and `value_sz`: scratch buffer for attr value extraction and reinsertion.

## API
- `xchk_xattr_set_map`
- `xchk_setup_xattr_buf`

## Notes
This header is shared by attr scrub and repair so both can reuse the same scratch allocation and byte-range validation helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.c

## Purpose
Repairs an inode’s extended attributes by salvaging valid-looking xattrs from damaged metadata, replaying them into a temporary file, and atomically exchanging the rebuilt attr fork into the target inode. It also handles live parent-pointer updates during repair.

## Main Entry Points
- `xrep_setup_xattr`: creates a temporary regular file and enables directory-entry gates when parent pointers exist.
- `xrep_xattr`: top-level repair.
- `xrep_xattr_reset_fork`: clears the target inode attr fork.
- `xrep_xattr_reset_tempfile_fork`: clears the tempfile attr fork after exchange.
- `xrep_xattr_swap`: exchanges or copies rebuilt attr fork contents.

## Key Behavior
Salvage stores attr records in `xfarray` and names/values in `xfblob`. Shortform entries, leaf local entries, and leaf remote entries have separate recovery paths. Remote values are retrieved with attr remote helpers, and corrupt remote values are quietly dropped if they fail checksum/corruption checks.

For non-inline attr forks, repair scans mapped attr fork extents and searches the buffer cache for possible leaf blocks. Because remote attr buffers can be multiblock and alias-prone, `xrep_xattr_find_buf` first looks for existing buffers in the range and otherwise reads one block with `XBF_TRYLOCK`; temporary single-block reads without buffer ops are staled before release.

To constrain memory, salvaged attrs are periodically flushed into the tempfile. Flushing commits the scrub transaction, drops ILOCKs, locks the tempfile with normal xattr IOLOCK semantics, inserts stashed attrs with `xfs_attr_set`, clears staging arrays, recreates the scrub transaction, and relocks the target.

Parent-pointer filesystems add a live dirent hook. While attr repair is flushing or exchanging, dirent updates pointing to the target inode are stashed as parent add/remove records and later replayed against the tempfile. If parent-pointer conflicts occur during a flush, repair can fully reset the tempfile and restart salvage with flushing disabled.

Final rebuild either removes the attr fork if no attrs were salvaged or finalizes the tempfile, replays all parent-pointer updates, prepares local forks for mapping exchange, exchanges attr fork mappings, reaps old attr fork blocks now attached to the tempfile, rolls transactions, unlocks the tempfile, and invalidates cached ACLs.

## Dependencies and Interactions
Requires rmapbt to reap old attr fork blocks and exchange-range support for atomic fork replacement. Uses tempfile, tempexch, xfile/xfarray/xfblob, attr, parent pointer, ACL, bmap, reap, and directory hook infrastructure.

## Failure Handling
Repair returns unsupported without rmapbt or exchange-range. Parent-pointer live update allocation failure marks repair aborted and causes `-EIO`. Staging allocations are torn down in all exit paths. If both original and tempfile attr forks are local and fit, repair avoids mapping exchange by copying local attr data directly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.h

## Purpose
Declares attr repair helper entry points used by other scrub repair code.

## API
- `xrep_xattr_swap`: exchange rebuilt tempfile attr fork with target attr fork.
- `xrep_xattr_reset_fork`: clear the target inode attr fork.
- `xrep_xattr_reset_tempfile_fork`: clear the tempfile attr fork after repair or cleanup.

## Notes
Forward-declares `struct xrep_tempexch` to avoid exposing tempfile exchange internals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.c

## Purpose
Implements sparse interval bitmaps for scrub and repair using Linux generic interval trees. It provides nearly identical 64-bit and 32-bit variants for filesystem block and per-AG/block/inode index use cases.

## Main APIs
For `xbitmap64`:
- `xbitmap64_init`, `xbitmap64_destroy`
- `xbitmap64_set`, `xbitmap64_clear`
- `xbitmap64_disunion`
- `xbitmap64_hweight`
- `xbitmap64_walk`
- `xbitmap64_empty`
- `xbitmap64_test`

For `xbitmap32`:
- `xbitmap32_init`, `xbitmap32_destroy`
- `xbitmap32_set`, `xbitmap32_clear`
- `xbitmap32_disunion`
- `xbitmap32_hweight`
- `xbitmap32_walk`
- `xbitmap32_empty`
- `xbitmap32_test`
- `xbitmap32_count_set_regions`

## Key Behavior
Each set region is an interval-tree node with start and inclusive last bit. `set` first clears overlap, then merges with left/right adjacent intervals or creates a new interval. `clear` handles four cases: split interval, trim left overlap, trim right overlap, or remove fully covered intervals. `disunion` applies logical `bitmap &= ~sub` by clearing every interval from `sub`.

`test` reports whether a requested start point is set and adjusts the supplied length to the contiguous set or clear run length before the next transition.

## Dependencies and Interactions
Used by many scrub repair modules to track sparse sets of blocks, AG blocks, fsblocks, and aginos via typed wrappers. Allocation uses `XCHK_GFP_FLAGS`.

## Failure Handling
Only interval split/set allocation can return `-ENOMEM`. Walk callbacks can stop iteration with any nonzero code; `-ECANCELED` is reserved by convention for intentional early stop.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.h

## Purpose
Declares sparse interval bitmap APIs for 64-bit and 32-bit ranges.

## Key Structures
- `struct xbitmap64`: cached rb-root storing 64-bit intervals.
- `struct xbitmap32`: cached rb-root storing 32-bit intervals.

## API Contracts
Iterator callbacks return 0 to continue and nonzero to stop; the stop value is propagated. Callers must not mutate a bitmap while walking it. `-ECANCELED` is documented as a safe sentinel for intentional cancellation because the bitmap walkers do not generate it themselves.

## Notes
This generic header underlies typed scrub bitmaps such as AG block, fsblock, and agino bitmap wrappers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bmap.c

## Purpose
Scrubs inode fork block mappings for data, attr, and CoW forks. It validates fork format, bmbt structure, incore extent records, physical target ranges, reverse mappings, realtime mappings, shared/CoW ownership, and special zapped-fork recovery signals.

## Main Entry Points
- `xchk_setup_inode_bmap`: obtains/locks inode, waits for DIO, flushes dirty data, invalidates page cache for repair, allocates scrub transaction, attaches dquots, and takes ILOCK.
- `xchk_bmap_data`
- `xchk_bmap_attr`
- `xchk_bmap_cow`

## Key Behavior
For btree-format forks, `xchk_bmap_btree` loads incore extents, checks btree blocks through generic btree scrub, verifies btree block owner fields on crc filesystems, and compares ondisk bmbt records to the incore extent tree unless the scrubber just loaded it.

The incore extent walk merges physically and logically contiguous mappings to reduce xref work. Each mapping is checked for order, logical range validity, dir/attr `xfs_dablk_t` addressability, physical data or realtime extent validity, and attr-fork prohibition on unwritten extents. Delalloc reservations are validated separately without disk xrefs.

Data/attr mappings are cross-referenced against rmapbt records with correct owner, offset, attr flag, unwritten flag, and non-bmbt flag. CoW fork mappings are checked against `XFS_RMAP_OWN_COW` and refcount CoW staging. Realtime mappings use rtgroup locking and rtrmap/refcount/bitmap helpers when available.

For apparently empty zapped data or attr forks, the scrubber can scan all AG or rtgroup reverse maps to detect rmaps that should have corresponding bmbt entries. This prevents a repaired-to-empty fork from being considered clean if rmaps still exist.

## Dependencies and Interactions
Uses inode locking, file writeback, bmbt, rmapbt/rtrmapbt, refcount, realtime group, health, and generic scrub btree helpers. Paired with `bmap_repair.c`.

## Failure Handling
Writeback `-ENOSPC` and `-EIO` do not stop metadata scrub. Broken xref trees are isolated through scrub xref processing. Zapped fork health flags are cleared only when scrub completes cleanly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bmap_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bmap_repair.c

## Purpose
Repairs inode data or attr fork block mappings by reconstructing bmap records from reverse mappings, preserving delalloc reservations, rebuilding the incore and optional ondisk bmbt fork, resetting inode block counters/quota, and reaping old bmbt blocks.

## Main Entry Points
- `xrep_bmap`: generic data/attr fork repair.
- `xrep_bmap_data`: data fork repair, allowing unwritten extents.
- `xrep_bmap_attr`: attr fork repair, rejecting unwritten extents.

## Key Behavior
Repair requires rmapbt. It scans realtime rmaps where relevant and all data-device AG rmaps, collecting records owned by the target inode. It accounts all inode-owned blocks for `i_nblocks`, but only converts rmaps for the selected fork into bmap records. BMBT block rmaps are recorded into `old_bmbt_blocks` for later reaping. Data fork delalloc reservations from the old incore extent tree are appended so repair does not lose pending allocations.

Each rmap is checked for obvious conflicts: valid AG/rtgroup range, valid file offset, no contradictory flags, not free space, not inode chunks, and realtime/data-device placement rules. Reconstructed mappings are split at `XFS_MAX_BMBT_EXTLEN`, converted to disk bmbt records, and sorted by file offset with overlap detection.

`xrep_bmap_build_new_fork` creates a staged fork via `xrep_newbt_init_inode`. If the number of real mappings fits in extents format, it loads an incore extent fork. Otherwise it computes btree geometry, reserves transaction space and new btree blocks, bulk-loads a staged bmbt, and loads the incore extent tree. It then commits the staged fork to the inode, updates `i_nblocks`, adjusts quota by the bmbt block delta, commits newbt reservations, rolls the transaction, and reaps old bmbt blocks.

For reflink filesystems, repair preserves an existing reflink inode flag and can discover shared extents while rebuilding a regular file data fork; if shared extents are found, it sets `XFS_DIFLAG2_REFLINK`.

## Dependencies and Interactions
Uses rmapbt/rtrmapbt, refcount, realtime groups, quota, bmbt staging, `xrep_newbt`, fsblock bitmap wrappers, `xfarray`, and reaping helpers. It assumes higher-level repair handles local/dev/uuid/meta-btree fork formats.

## Failure Handling
Unsupported without rmapbt. Non-repairable fork formats return no work or corruption depending on format. All newbt state is canceled on failure, old block bitmap and mapping arrays are destroyed, and old bmbt blocks are reaped only after the new fork is committed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/bmap_repair.c -->