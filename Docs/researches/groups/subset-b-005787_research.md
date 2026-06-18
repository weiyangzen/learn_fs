# subset-b-005787 XFS scrub research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader.c

## Purpose
This file implements online scrub validation for XFS allocation group headers: secondary superblocks, AGF, AGFL, and AGI. It verifies on-disk header geometry against the mounted primary superblock, checks per-AG counter consistency, validates btree roots and levels, and cross-references header blocks and AGFL entries against free-space, inode, rmap, refcount, shared, and CoW-staging metadata.

## Important APIs, types, and functions
`xchk_setup_agheader` prepares filesystem-level scrub and enables intent draining when required. `xchk_superblock` reads secondary superblocks with `xfs_sb_read_secondary`, compares fixed mkfs geometry as corruption and mutable propagated fields as preen candidates, and uses `xchk_superblock_ondisk_size` to ensure trailing bytes are zero for the active feature set. `xchk_agf`, `xchk_agfl`, and `xchk_agi` are the public scrub entry points for AGF, AGFL, and AGI. Helper cross-reference functions include `xchk_superblock_xref`, `xchk_agf_xref_*`, `xchk_agfl_xref`, `xchk_agfl_block_xref`, and `xchk_agi_xref_*`. `struct xchk_agfl_info` tracks expected AGFL count, discovered entries, uniqueness array, and buffers.

## Control flow and state
Header scrub normally reads the target AG headers through `xchk_ag_read_headers` or specific read helpers, rechecks verifiers with `xchk_buffer_recheck`, validates scalar fields, and only then performs cross-reference checks if the main corruption flag is still clear. AGF validation checks length, bnobt/cntbt/rmapbt/refcountbt roots and levels, AGFL circular counters, and in-core `pagf_*` counters. AGFL validation reads AGF and AGFL, walks active AGFL entries, records them into a temporary array, verifies count, sorts, and detects duplicates. AGI validation checks length, inobt/finobt roots and levels, inode counters, newino/dirino, unlinked buckets, padding, in-core `pagi_*` counters, and the in-memory iunlink chain.

## Persistence and integration
The file is read-only validation except for scrub state flags. It depends on mounted primary superblock data, perag state, buffer verifiers, btree cursors, and xref helpers from scrub common code. It integrates with online repair by setting corrupt or preen flags that later repair code consumes, and with health tracking through scrub result flags.

## Risks and test signals
Key risks are feature-gated superblock field comparisons, circular AGFL counter math, races with AG teardown, and xref checks that must degrade cleanly if btree cursors cannot be trusted. Useful tests include corrupt secondary superblock variants, stale mutable secondary superblock fields, invalid AGF roots/levels, inconsistent AGF counters versus btrees and perag state, duplicate or out-of-range AGFL entries, broken AGI unlinked bucket chains, and xref failure injection for missing btree cursors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader_repair.c

## Purpose
This file repairs AG header structures: secondary superblocks, AGF, AGFL, and AGI. The design uses reliable metadata such as the primary superblock, rmapbt records, live btrees, incore inode state, and temporary bitmaps/arrays to reconstruct damaged headers, commit them transactionally, and refresh per-AG in-core counters.

## Important APIs, types, and functions
`xrep_superblock` rewrites a secondary superblock from `mp->m_sb`, clearing secondary-ignored NEEDSREPAIR and log incompat flags. `xrep_agf` reconstructs AGF roots and counters using `xrep_find_ag_btree_roots`, `xrep_agf_set_roots`, and `xrep_agf_calc_from_btrees`. `xrep_agfl` rebuilds the AGFL from OWN_AG rmap records after subtracting actual btree metadata and crosslinked blocks. `xrep_agi` rebuilds AGI btree roots, inode counters, and iunlink lists. `struct xrep_agi` stores AGI repair context, old header backup, staged iunlink heads, `xagino_bitmap`, and `xfarray` maps for next/prev iunlink pointers. `struct xrep_agfl` and `struct xrep_agfl_fill` manage AGFL block collection and formatting.

## Control flow and state
AGF repair requires rmapbt support. It reads the raw AGF, reads and sanity-checks AGFL, finds btree roots, takes a final termination checkpoint, rewrites the AGF header, implants roots, recalculates counters from btrees, logs the buffer, updates `pagf_*`, sets `XFS_AGSTATE_AGF_INIT`, and rolls the AG transaction. AGFL repair derives candidate blocks from OWN_AG mappings, removes currently used btree blocks and crosslinked blocks, writes a new AGFL, updates AGF flcount/first/last, rolls the transaction, and reaps overflow blocks. AGI repair finds inobt/finobt roots, reconstructs iunlink state from ondisk buckets, incore inode cache, and ondisk inode scans, then rewrites header fields, counters, and unlinked bucket heads.

## Persistence and integration
All repairs are transactional and use buffer type tagging plus `xfs_trans_log_buf` or inode logging helpers. Perag initialization bits are cleared while headers are unsafe and set after reinitialization. Summary counters are forced to recalc after AGF/AGI changes. AGFL overflow and stale metadata are returned through reap helpers, which depend on accurate rmap ownership.

## Risks and test signals
The principal risk is chicken-and-egg reconstruction: AGF and AGFL both depend on rmapbt and AGFL data even when headers are damaged. AGI iunlink repair is sensitive to races, cached inode lifetime, and correct forward/back pointer logging. Tests should cover missing rmapbt rejection, bad AGFL candidates, refcount feature root handling, AGF counter recomputation, iunlink cycles or wrong buckets, uncached unlinked inodes, transaction roll failures, and rollback paths that restore old headers after calculation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agino_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/agino_bitmap.h

## Purpose
This header provides a type-checked bitmap wrapper for per-AG inode numbers (`xfs_agino_t`). It narrows the generic 32-bit sparse bitmap API to AG inode number use sites, mostly repair code that tracks sets of inodes inside one allocation group.

## Important APIs, types, and functions
`struct xagino_bitmap` embeds `struct xbitmap32 aginobitmap`. Inline functions mirror the generic bitmap operations: `xagino_bitmap_init`, `xagino_bitmap_destroy`, `xagino_bitmap_clear`, `xagino_bitmap_set`, `xagino_bitmap_test`, and `xagino_bitmap_walk`. The walk callback type is inherited from `xbitmap32_walk_fn`.

## Control flow and state
There is no independent control flow; all functions immediately delegate to `xbitmap32`. State is the interval tree maintained by the underlying bitmap. Callers pass AG inode start and length values, and the wrapper preserves those types at the interface boundary.

## Persistence and integration
The structure is in-memory only and must be initialized and destroyed by the caller. It integrates with AGI repair, especially iunlink reconstruction, where sets of unlinked, missing, or already-processed AG inode numbers are tracked compactly.

## Risks and test signals
The header relies on the underlying `xbitmap32` semantics, including interval merging, splitting, and walk immutability. Tests should focus on callers: setting, clearing, and walking sparse AG inode ranges; ensuring no full inode numbers are accidentally passed; and verifying cleanup on repair abort paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agino_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc.c

## Purpose
This file scrubs the XFS free-space btrees: bnobt ordered by block number and cntbt ordered by length. It validates individual free-space records, checks that matching records exist in the sibling free-space tree, detects mergeable adjacent records, and exposes a shared xref helper to verify that a block range is not free.

## Important APIs, types, and functions
`xchk_setup_ag_allocbt` prepares AG btree scrub, enables intent draining if needed, and invokes `xrep_setup_ag_allocbt` when repair might run. `xchk_allocbt` selects `sc->sa.bno_cur` or `sc->sa.cnt_cur` based on scrub type and runs `xchk_btree`. `xchk_allocbt_rec` decodes `xfs_alloc_rec_incore` records and validates them with `xfs_alloc_check_irec`. `xchk_allocbt_xref_other` confirms the corresponding record exists in the other free-space btree. `xchk_allocbt_mergeable` preens corruption when adjacent records could be coalesced. `xchk_xref_is_used_space` is a reusable xref helper used by many scrubbers.

## Control flow and state
Setup locks the AG btree context. Record scrub decodes each btree record, validates extent bounds, checks local ordering through `struct xchk_alloc.prev`, cross-references the peer tree, ensures the free space is not an inode chunk, has no rmap owner, is not shared, and is not CoW staging. The scrub stops marking deeper xref findings once global corruption is already present.

## Persistence and integration
The file does not mutate filesystem metadata. It depends on AG btree cursors, inode allocation xrefs, rmap ownership checks, refcount checks, and common btree scrub machinery. Its `xchk_xref_is_used_space` helper is central to header, bmap, and metadata scrubbers that need to prove their blocks are allocated.

## Risks and test signals
Risks include incorrect peer-tree matching between differently ordered trees, failing to flag mergeable free records, and suppressing xrefs too aggressively when one cursor fails. Tests should cover malformed alloc records, adjacent free extents that should merge, bnobt/cntbt mismatches, free extents overlapping inode chunks or shared/COW space, and `xchk_xref_is_used_space` behavior for empty, full, and partially overlapping record packing outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc_repair.c

## Purpose
This file repairs the bnobt and cntbt simultaneously. It reconstructs free-space records by scanning reverse mappings for gaps and OWN_AG metadata, stages new free-space btrees with the newbt framework, updates AGF counters, and reaps blocks from the old allocation btrees.

## Important APIs, types, and functions
`struct xrep_abt` holds the repair state: bitmaps for old allocbt blocks and non-allocbt OWN_AG blocks, staged new bnobt/cntbt builders, an `xfarray` of free records, cursor position, free block counters, and longest extent. `xrep_setup_ag_allocbt` flushes busy extents before repair. `xrep_abt_find_freespace` scans rmapbt and AGFL data. `xrep_abt_reserve_space` reserves free extents for new btree blocks through an iterative geometry calculation. `xrep_abt_build_new_trees` sorts, reserves, bulk-loads cntbt and bnobt, commits staged roots, and resets AGF counters. `xrep_allocbt` is the repair entry point, and `xrep_revalidate_allocbt` re-scrubs both trees.

## Control flow and state
Repair requires rmapbt. It first ensures the busy extent list is empty to avoid double-use of blocks. Rmap walking records gaps as free records, records OWN_AG blocks as possible old allocbt blocks, and records rmapbt path blocks plus AGFL entries as blocks that must not be released. After subtracting the not-allocbt bitmap, remaining OWN_AG blocks are candidates for old bnobt/cntbt blocks. Free records are sorted by length to reserve btree blocks efficiently, may be shrunk or removed to satisfy staged btree reservations, then are sorted appropriately for cntbt and bnobt bulk loading.

## Persistence and integration
The new trees are installed via staged btree commit helpers, AGF fields `agf_btreeblks`, `agf_freeblks`, and `agf_longest` are logged, perag btree heights are reinitialized, and transaction rolls make new roots durable before old blocks are reaped. Rmap updates and free of unused reservations use deferred operations.

## Risks and test signals
The repair depends on rmap correctness and must handle reflink-overlapping rmap records. Reservation logic can consume free records and alter sorting, making off-by-one and ENOSPC behavior important. Tests should include maximally fragmented AGs, no-space repairs, reflink overlap gaps, AGFL-owned OWN_AG subtraction, stale btree block reaping, btree height changes that exercise alternate verifier heights, busy extent refusal, and revalidation of both trees after repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.c

## Purpose
This file scrubs extended attribute metadata for an inode. It validates shortform and leaf/block attr structures, checks name/value placement with byte bitmaps, verifies hashes and namespaces, retrieves every attribute by name/hash, and validates parent pointer values.

## Important APIs, types, and functions
`xchk_setup_xattr` prepares repair state when available, optionally preallocates maximum buffers for retry, and sets up inode-content scrub. `xchk_setup_xattr_buf` manages `struct xchk_xattr_buf`, including used/free maps, salvage name buffer, and value buffer. `xchk_xattr_set_map` marks byte ranges and detects overlaps/out-of-bounds usage. `xchk_xattr_actor` is called by attr walking to validate names, parent values, lookupability, and value length. `xchk_xattr_block`, `xchk_xattr_entry`, and `xchk_xattr_rec` validate attr leaf internals. `xchk_xattr_check_sf` validates shortform attr layout. `xchk_xattr` is the main entry point.

## Control flow and state
Scrub allocates reusable buffers, validates physical structure first, then does semantic lookup of every xattr if no corruption was found. Shortform validation walks entries inside the inode fork and marks each header/name/value byte range. Leaf validation clears used/free maps per block, validates padding, header bounds, entry array placement, sorted hashes, local versus remote entry sizes, freemap entries, and `usedbytes`. Record validation recalculates the attr hash from local value bytes or remote value length and checks namespace flags. The actor path fetches values with `xfs_attr_get_ilocked` to ensure dabtree lookup and remote value retrieval work.

## Persistence and integration
This file is validation-only, except for scrub result flags and preen markers for incomplete attrs, leaf holes, and harmless freemap anomalies. It integrates with dabtree scrub, listxattr walking, parent pointer validation, attr repair buffers, and inode locking established by setup.

## Risks and test signals
Risks center on byte map bounds, remote value lookup, parent pointer validation, and avoiding deadlocks by returning `-EDEADLOCK` when larger buffers are needed. Tests should cover malformed shortform sizes, overlapping attr entries, bad freemap/usedmap intersections, unsorted hashes, wrong namespace flags, invalid parent pointer values, missing remote value blocks, lookup returning `-ENODATA`, incomplete attrs being preened, and retry with `XCHK_TRY_HARDER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.h

## Purpose
This header declares the temporary buffer shared by extended attribute scrub and repair. It centralizes the in-memory maps and scratch buffers required to validate attr block layout, retrieve values, and salvage names/values during repair.

## Important APIs, types, and functions
`struct xchk_xattr_buf` contains `usedmap`, `freemap`, `name`, `value`, and `value_sz`. `xchk_xattr_set_map` marks byte ranges in leaf or shortform buffers. `xchk_setup_xattr_buf` allocates or resizes the scratch storage.

## Control flow and state
The buffer is owned through `sc->buf` and cleaned through `sc->buf_cleanup`. `usedmap` is mandatory for structural validation; `freemap` is allocated only when deep checking is needed or leaf blocks may exist. `name` is allocated when repair may need to reconstruct attributes. `value` grows on demand and contents are not preserved across resize.

## Persistence and integration
All state is temporary. The header is consumed by `attr.c` for validation and by `attr_repair.c` for salvage and reinsertion into temporary files. The structure deliberately avoids embedding filesystem metadata ownership; callers derive all context from `xfs_scrub`.

## Risks and test signals
The main risks are buffer reuse after resize, cleanup omissions, and callers assuming `freemap` or `name` exists without satisfying setup conditions. Tests should exercise repeated setup calls with increasing value sizes, repair versus no-repair allocation paths, try-harder allocation of maximum attr size, and cleanup after partial allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.c

## Purpose
This file repairs an inode's extended attributes by salvaging readable xattr entries from damaged metadata, rebuilding them in a temporary file, and atomically exchanging the rebuilt attr fork into the target inode. It also handles parent pointer filesystems by capturing concurrent dirent updates and replaying them into the temporary attr fork.

## Important APIs, types, and functions
`struct xrep_xattr` is the main repair context, holding tempfile exchange state, `xfarray`/`xfblob` salvage stores, parent pointer replay stores, a dirent hook, and scratch name/value buffers. `xrep_setup_xattr` creates the tempfile and enables dirent gating for parent pointers. Salvage helpers include `xrep_xattr_recover_sf`, `xrep_xattr_recover_leaf`, `xrep_xattr_recover_block`, and local/remote attribute salvage functions. `xrep_xattr_flush_stashed` periodically inserts salvaged attrs into the tempfile. `xrep_xattr_rebuild_tree`, `xrep_xattr_swap`, `xrep_xattr_reset_fork`, and `xrep_xattr_reset_tempfile_fork` commit or clean up forks. `xrep_xattr` is the repair entry point.

## Control flow and state
Repair rejects files without attrs and requires rmapbt plus exchange-range support. It sets up staging arrays, blobs, and optional parent pointer hooks. Shortform attrs are recovered directly from the fork; block-format attrs are scanned by extent mapping, buffer-cache probing, and leaf structure checks. Salvaged attrs are stored as keys plus blob-backed names/values, then flushed to the tempfile to cap memory at roughly eight pages. If parent pointer updates arrive during flushing, repair can reset the tempfile and restart without intermediate flushing. Finalization replays all queued parent pointer changes, prepares local forks for exchange if needed, swaps attr fork mappings, reaps the tempfile's old fork, and invalidates cached ACLs.

## Persistence and integration
The repair crosses several persistence domains: scrub transaction for salvage, ordinary attr transactions for tempfile insertion, atomic extent exchange for final commit, and reap helpers for old attr blocks. Locking deliberately moves between target inode ILOCK/IOLOCK and tempfile locks. Parent pointer updates are observed through `xfs_dir_hook`.

## Risks and test signals
Risks include aliased remote value buffers, live parent pointer update races, duplicate salvaged attrs, partial tempfile resets, and local-to-leaf conversion before exchange. Tests should cover damaged shortform and leaf attrs, corrupt remote value blocks, millions of attrs triggering flushes, parent pointer add/remove during repair, reset/restart after conflict, no-salvage attr fork removal, ACL cache invalidation, exchange failure cleanup, and unsupported-feature returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.h

## Purpose
This header exposes the small public interface for extended attribute repair operations that other repair modules need. It avoids publishing the large salvage context and keeps tempfile exchange details mostly private to `attr_repair.c`.

## Important APIs, types, and functions
It forward-declares `struct xrep_tempexch` and declares `xrep_xattr_swap`, `xrep_xattr_reset_fork`, and `xrep_xattr_reset_tempfile_fork`. The swap API commits a rebuilt tempfile attr fork into the target inode. The reset APIs clear attr forks from the target inode or tempfile.

## Control flow and state
There is no implementation state in this header. The functions require callers to hold the locks and transaction context documented by `attr_repair.c`; incorrect call context can corrupt fork state or violate exchange preconditions.

## Persistence and integration
These APIs are used by broader inode repair flows that need to reset or exchange attribute forks after other metadata reconstruction. They integrate with tempfile exchange and attr fork reaping code.

## Risks and test signals
Tests should focus on call-site locking and transaction requirements: resetting a target attr fork with extents, resetting a tempfile attr fork before inactivation, swapping local-local forks by copyout, swapping block-mapped forks through `xrep_tempexch_contents`, and confirming old attr blocks are left attached to the tempfile for reaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.c

## Purpose
This file implements sparse interval bitmaps for 64-bit and 32-bit address spaces using Linux interval-tree/rbtree infrastructure. Scrub and repair use these structures to collect ranges of filesystem blocks, AG blocks, inode numbers, or other dense numeric spaces without allocating full bit arrays.

## Important APIs, types, and functions
For 64-bit ranges, `struct xbitmap64_node` stores start, last, and subtree-last fields, and public operations are `xbitmap64_init`, `destroy`, `set`, `clear`, `disunion`, `hweight`, `walk`, `empty`, and `test`. The 32-bit implementation mirrors the same API with `struct xbitmap32_node`, plus `xbitmap32_count_set_regions`. Both use `INTERVAL_TREE_DEFINE` to generate tree operations.

## Control flow and state
`set` first checks if a range is already covered, clears overlapping intervals, then merges with left and/or right adjacent intervals or inserts a new node. `clear` removes or splits overlapping intervals depending on whether the clear range covers the middle, left, right, or whole interval. `disunion` iterates all ranges in the subtracting bitmap and clears them from the target. `walk` calls the caller callback for every set interval and stops on any nonzero return. `test` reports whether the requested start is set and adjusts length to the contiguous state run.

## Persistence and integration
The bitmaps are in-memory only and require explicit destruction. They are foundational for repair paths that compute stale metadata blocks, free-space gaps, AGFL candidates, iunlink inode sets, and bmap old-block sets through typed wrappers such as `xagb_bitmap`, `xfsb_bitmap`, and `xagino_bitmap`.

## Risks and test signals
Critical risks are integer overflow in `start + len - 1`, adjacency around zero or max values, split allocation failure leaving partial state, and modifying a bitmap during walk. Tests should cover set/clear inside, outside, and across intervals; merging both neighbors; disunion of overlapping and empty sets; hweight overflow boundaries; early walk cancellation with `-ECANCELED`; and `test` length adjustment for set and clear runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.h

## Purpose
This header declares sparse bitmap APIs for 64-bit and 32-bit range sets used by XFS scrub and repair. It defines the storage wrapper types and the callback contracts for iterating set intervals.

## Important APIs, types, and functions
`struct xbitmap64` and `struct xbitmap32` both contain an `rb_root_cached`. The declared operations initialize, destroy, set, clear, subtract (`disunion`), count set bits (`hweight`), walk intervals, test a range prefix, and check emptiness. `xbitmap32_count_set_regions` additionally counts intervals. `xbitmap64_walk_fn` and `xbitmap32_walk_fn` define the callback signatures.

## Control flow and state
The header documents that walk callbacks return zero to continue and nonzero to stop, and reserves `-ECANCELED` as a caller-directed early-stop value. Callers must not modify the bitmap while walking it. The actual tree state and interval coalescing are private to `bitmap.c`.

## Persistence and integration
The API is purely in-memory. It is used directly and through typed wrappers for AG blocks, filesystem blocks, and AG inode numbers. Repair code relies on stable interval semantics to subtract live metadata from broad ownership scans before reaping suspected stale blocks.

## Risks and test signals
Risks are mostly API misuse: forgetting `destroy`, using nonpositive lengths, assuming callbacks can mutate the tree, and treating `hweight` as interval count. Tests should validate callback early-stop propagation, empty bitmap behavior, 32-bit and 64-bit boundary ranges, and wrapper-specific type conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap.c

## Purpose
This file scrubs inode block mappings for data, attribute, and CoW forks. It validates fork formats, bmap btree records, in-core extent cache records, delalloc reservations, and cross-references mappings against allocation, inode, reverse mapping, refcount, CoW staging, and realtime metadata.

## Important APIs, types, and functions
`xchk_setup_inode_bmap` obtains and locks the inode, flushes regular file state, waits for direct I/O, optionally invalidates page cache for repair, allocates a transaction, attaches quotas, and takes ILOCK. `struct xchk_bmap_info` tracks scrub context, cursor, previous record, fork, realtime/shared flags, and whether extents were loaded. `xchk_bmap` is the shared scrub driver; `xchk_bmap_data`, `xchk_bmap_attr`, and `xchk_bmap_cow` are public entry points. Helpers include `xchk_bmap_btree`, `xchk_bmapbt_rec`, `xchk_bmap_iext_iter`, datadev/realtime xref functions, rmap exact-match checks, and empty-fork rmap scans.

## Control flow and state
Setup stabilizes ephemeral writes before inspecting mappings. The scrub driver rejects impossible fork formats, scans the bmbt if the fork is in btree format, then iterates the in-core extent list. The iterator merges logically and physically contiguous mappings to reduce xref work and preens files that could use fewer bmbt records. Real extents are validated for file range, physical range, unwritten rules, directory/attr dablock addressability, and then cross-referenced. Delalloc extents are validated only for logical range and maximum bmbt length. If a fork appears zapped, optional rmap scans verify whether rmaps still exist for the inode.

## Persistence and integration
This file is read-only validation, but it flushes data and can invalidate page cache before repair. It integrates with AG and realtime group scrub state, rmap/refcount btrees, health flags for zapped forks, quota setup, inode locks, and btree scrub. It understands reflink sharing and COW staging ownership distinctions.

## Risks and test signals
Risks include stale in-core extent cache versus disk btree, delalloc handling, realtime group boundaries, reflink rmap lookup semantics, and empty-fork recovery heuristics. Tests should cover btree owner mismatches, bmbt/incore divergence, contiguous merge preen, attr fork unwritten extents, COW fork on non-reflink filesystems, zapped data/attr forks with rmap residue, realtime rmap/refcount xrefs, shared data fork extents, and writeback errors during setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap_repair.c

## Purpose
This file repairs an inode data or attr fork block map by reconstructing mappings from reverse mapping records. It builds a new in-core extent tree and, when needed, a new bmap btree; updates inode block counts, quota counts, and reflink flags; and reaps blocks from the old bmbt.

## Important APIs, types, and functions
`struct xrep_bmap` stores old bmbt block bitmap, newbt state, collected bmap records, block counters, fork selection, reflink scan state, and unwritten-extent policy. `xrep_bmap` is the shared repair entry point, with `xrep_bmap_data` and `xrep_bmap_attr` wrappers. Collection helpers include `xrep_bmap_scan_ag`, `xrep_bmap_scan_rtgroup`, `xrep_bmap_walk_rmap`, `xrep_bmap_walk_rtrmap`, and `xrep_bmap_find_delalloc`. Build helpers include `xrep_bmap_sort_records`, `xrep_bmap_extents_load`, `xrep_bmap_btree_load`, `xrep_bmap_build_new_fork`, and `xrep_bmap_remove_old_tree`.

## Control flow and state
Input checks require rmapbt and accept only extents or btree fork formats. Repair allocates an `xfarray` sized to the maximum fork extent count, scans realtime rmaps and per-AG rmaps, validates every candidate rmap against allocation and inode metadata, records all blocks for `i_nblocks`, records old bmbt blocks, and converts fork rmaps into bmbt records split at `XFS_MAX_BMBT_EXTLEN`. Delalloc reservations from the old in-core tree are preserved. Records are sorted by logical offset and checked for overlap. The new fork is staged as extents if it fits or as a bulk-loaded btree otherwise, then committed into the inode.

## Persistence and integration
The repair joins the inode to the transaction, reserves blocks for a new btree as needed, commits staged btree/fork roots, logs inode core changes, updates quota block counts by the bmbt-size delta, commits newbt reservations, rolls transactions, and reaps old bmbt blocks using the correct owner info. Reflink state is recalculated by consulting refcount records for discovered shared extents.

## Risks and test signals
Risks include trusting damaged rmap records, reconstructing realtime and datadev mappings together, preserving delalloc correctly, setting `XFS_DIFLAG2_REFLINK` only when warranted, and keeping `i_nblocks`/quota accurate after btree size changes. Tests should include zapped forks rebuilt from rmap, attr fork rejecting unwritten extents, realtime data mappings, old bmbt block reaping, large extent counts, split records above max bmbt length, overlap detection after sort, non-file data fork rejection, shared extent reflink flag discovery, and failure cleanup for newbt reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap_repair.c -->
