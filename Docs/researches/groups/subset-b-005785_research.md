# subset-b-005785 research

Grouped research for XFS libxfs reference count, reverse mapping, and realtime bitmap files under `sources/distributed-fs/ceph-client/fs/xfs/libxfs`. Each section preserves the source path in its title and is wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.c

## Purpose
`xfs_refcount.c` implements the shared-block and copy-on-write reference count logic for XFS reflink filesystems. It is the high-level editor for refcount btree records, converting file extent mapping changes into persistent per-AG or per-realtime-group refcount records. Shared extents are represented only when `rc_refcount >= 2`; in-progress COW staging extents are deliberately represented as domain-specific records with refcount 1 so that crash recovery can find and free orphaned COW allocations.

## Important APIs, types, and functions
The exported lookup/query primitives are `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_get_rec`, `xfs_refcount_insert`, `xfs_refcount_has_records`, and `xfs_refcount_query_range`. They are thin wrappers over generic btree operations, but they set `cur->bc_rec.rc` and validate decoded records before exposing them to callers.

Mutation is staged through `struct xfs_refcount_intent` instances allocated from `xfs_refcount_intent_cache`. `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`, `xfs_refcount_alloc_cow_extent`, and `xfs_refcount_free_cow_extent` enqueue deferred operations; `xfs_refcount_finish_one` and `xfs_rtrefcount_finish_one` execute those operations against an AG refcountbt cursor or realtime refcountbt cursor. COW allocation/free helpers also schedule matching rmap operations with `XFS_RMAP_OWN_COW`.

Internal helpers implement record surgery: `xfs_refcount_split_extent` splits records crossing an operation boundary; `xfs_refcount_find_left_extents` and `xfs_refcount_find_right_extents` synthesize implicit refcount-1 gaps; `xfs_refcount_merge_extents` tries center/left/right merges; `xfs_refcount_adjust_extents` performs the actual increment/decrement; and `xfs_refcount_adjust_cow_extents` adds or removes COW-domain records.

## Control flow
For normal shared-block changes, callers enqueue an increase or decrease intent. The finisher creates or reuses a cursor for the correct AG/RTG, converts the filesystem block to a group block, and calls `xfs_refcount_adjust`. Adjustment first splits any records crossing the left and right operation boundaries, then attempts boundary merges, then walks the remaining interval. Missing records inside the interval are treated as implicit refcount 1 because a file mapping already proves the blocks are allocated. Incrementing such a gap inserts a shared-domain record with refcount 2; decrementing a shared record to 1 deletes it; decrementing below 1 schedules the underlying blocks for free through `xfs_free_extent_later`.

COW staging follows the same split/merge shape, but operates in `XFS_REFC_DOMAIN_COW` and enforces exact allocation/free matches. `__xfs_refcount_cow_alloc` requires no overlapping COW record; `__xfs_refcount_cow_free` requires an exact refcount-1 COW record. `xfs_refcount_recover_cow_leftovers` scans the COW domain at mount/recovery time, gathers all orphaned COW records in an empty transaction to avoid buffer deadlocks, then commits real transactions that remove the COW record and free the physical blocks.

## State and persistence behavior
Persistent state is the refcount btree itself, plus deferred-intent log items created by the refcount item layer. Shared records encode domain in the high startblock bit via `xfs_refcount_encode_startblock`; record bodies store startblock, blockcount, and refcount. The code relies on transaction logging through the generic btree layer, and free operations are deferred with `xfs_free_extent_later`. The finisher may leave an intent partially complete by updating `ri_startblock` and `ri_blockcount` if the transaction reservation is nearly exhausted, as estimated by `xfs_refcount_still_have_space`.

Realtime refcount operations parallel the AG implementation but lock and join the realtime group with `XFS_RTGLOCK_REFCOUNT`, use `xfs_rtrefcountbt_init_cursor`, and validate ranges with `xfs_verify_rgbext` / `xfs_verify_rtbext`.

## Dependencies and integration points
This file depends on generic btree operations, refcount btree cursor construction, realtime refcount btree support, deferred operation infrastructure, block allocation/freeing, rmap updates, AG/RTG locking, tracing, error tags, and health marking. It is called from bmap/reflink paths that map, unmap, share, unshare, and complete COW extents. It also feeds scrub/repair through range query and `has_records` helpers.

## Risks and invariants
Key risks are off-by-one interval handling, implicit refcount-1 gap synthesis, overflow around `XFS_REFC_LEN_MAX`, and transaction reservation underestimation. Corruption checks enforce nonzero bounded blockcount, valid domain/refcount combinations, valid AG/RTG ranges, exact insert/delete success counts, and exact COW frees. Records with `XFS_REFC_REFCOUNT_MAX` are pinned and no longer incremented, which is an intentional saturation behavior.

## Test signals
Useful coverage includes reflink copy/unshare workloads, COW writeback crash recovery, log recovery with pending refcount intents, realtime reflink operations, forced transaction continuations via `XFS_ERRTAG_REFCOUNT_CONTINUE_UPDATE`, and corruption tests that inject malformed records or boundary-crossing extents. Tracepoints such as `trace_xfs_refcount_modify_extent`, finisher leftovers, and btree sick markings are important diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.h

## Purpose
`xfs_refcount.h` declares the public libxfs interface for refcount btree lookup, update intents, COW reservation tracking, query callbacks, and validation. It is the contract between bmap/reflink/defer code and the refcount implementation.

## Important APIs and types
The header exposes lookup/get functions, `xfs_refcount_insert`, range query, `xfs_refcount_has_records`, per-AG and realtime record validators, and `xfs_refcount_btrec_to_irec`. `enum xfs_refcount_intent_type` defines deferred operation types: increase, decrease, allocate COW, and free COW. `struct xfs_refcount_intent` carries the deferred list node, target `xfs_group`, operation type, blockcount, startblock, and realtime flag.

`xfs_refcount_encode_startblock` is a central inline helper that folds the refcount domain into the high startblock bit. `xfs_refcount_check_domain` encodes a core invariant: COW-domain records must have refcount 1, while shared-domain records must have refcount at least 2.

## Control flow and integration
Callers should enqueue logical operations through `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`, `xfs_refcount_alloc_cow_extent`, and `xfs_refcount_free_cow_extent`; deferred processing calls `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`. Query users provide an `xfs_refcount_query_range_fn` callback and receive validated in-core records.

## State and persistence behavior
The header does not store state itself, but defines the in-memory deferred operation shape that backs logged refcount intent items. The `XFS_REFCOUNT_ITEM_OVERHEAD` estimate documents how much log reservation each dirty refcount record is assumed to consume, including space for split/continuation behavior.

## Dependencies, risks, and test signals
The API depends on `xfs_btree_cur`, `xfs_trans`, `xfs_bmbt_irec`, `xfs_perag`, and `xfs_rtgroup`. Callers must pass group-relative block ranges of the correct domain, avoid using COW fork mappings for normal refcount updates, and expect operations to be continued across transactions. Tests should verify domain encoding, saturation behavior, deferred intent replay, and COW record validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.c

## Purpose
`xfs_refcount_btree.c` implements the per-AG refcount btree geometry and generic btree operation table. It does not perform high-level refcount interval editing; instead, it tells the generic btree code how to allocate/free refcountbt blocks, compare keys, verify blocks, initialize cursors, compute tree height/size, and commit staged repair trees.

## Important APIs and functions
The main exported entry points are `xfs_refcountbt_init_cursor`, `xfs_refcountbt_commit_staged_btree`, `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`, `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, `xfs_refcountbt_calc_reserves`, `xfs_refcountbt_maxlevels_ondisk`, and the cursor cache init/destroy functions.

The `xfs_refcountbt_ops` table provides callbacks for cursor duplication, root updates, block allocation/freeing, min/max record counts, key/record initialization, comparison, verifier operations, ordering, and key contiguity. `xfs_refcountbt_buf_ops` wires the CRC and structural verifiers into buffer I/O.

## Control flow
When btree shape changes need a new block, `xfs_refcountbt_alloc_block` allocates one metadata-reserved block near the refcount btree area, records ownership as `XFS_RMAP_OINFO_REFC`, increments `agf_refcount_blocks`, and logs the AGF field. Freeing decrements the block count and schedules the btree block for deferred freeing with refcount owner info. Root changes update `agf_refcount_root` and `agf_refcount_level`, mirror the level into `pagf_refcount_level`, and log root/level fields.

Cursor initialization allocates from `xfs_refcountbt_cur_cache`, holds the AG group, attaches the AGF buffer when available, and initializes `bc_refc.nr_ops` / `shape_changes`. Staged repair commits replace root, level, and block count from the fake root and then ask generic btree staging code to finish.

## State and persistence behavior
Persistent state is held in AGF fields: `agf_refcount_root`, `agf_refcount_level`, and `agf_refcount_blocks`, plus the btree blocks themselves. Block verification requires reflink support, valid v5 AG btree headers, sane level bounds, and generic btree block consistency with mount record geometry. Writes recalculate the AG btree CRC.

## Dependencies and integration points
This file integrates with `xfs_alloc`, `xfs_rmap`, `xfs_btree`, `xfs_btree_staging`, AG health, tracing, and mount geometry setup. `xfs_refcount.c` relies on this cursor implementation for all per-AG refcount mutations, while repair code uses staged commit support.

## Risks and test signals
Risks include mismatched AGF counters, root/level updates not logged, invalid maxlevel computation for extreme AG sizes, and verifier behavior during online repair. Tests should exercise btree block split/merge, reserve calculations with an internal log AG, online repair staged-tree commit, bad magic/CRC/level verifier failures, and disabled-reflink mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.h

## Purpose
`xfs_refcount_btree.h` declares the on-disk refcount btree block layout helpers and the public cursor/geometry functions for per-AG refcount btrees.

## Important APIs and layout
`XFS_REFCOUNT_BLOCK_LEN` defines the v5 short btree header size. `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, and `XFS_REFCOUNT_PTR_ADDR` compute record, key, and pointer addresses inside a refcountbt block; these macros are also part of the userspace-visible libxfs contract. The header declares cursor creation, max records, maxlevels computation, size/reserve calculations, staged-tree commit, and cursor-cache lifecycle functions.

## Control flow and state
The declarations support three main flows: normal refcount update cursors, mount-time geometry/reservation setup, and online repair staging. Persistent state is still AGF-rooted, but this header defines how code accesses btree block interiors and asks the implementation to compute space requirements.

## Dependencies, risks, and test signals
The header depends on generic XFS btree types, mount/perag types, and staged fake roots. Address macros must match the on-disk format exactly; any mismatch corrupts userspace tools and kernel traversal. Tests should include block layout validation across leaf and internal nodes, min block size geometry, and staged repair commit callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.c

## Purpose
`xfs_rmap.c` implements reverse mapping btree record lookup, validation, mutation, deferred intent finishing, and query helpers. Reverse mappings record who owns physical blocks, enabling metadata repair, online scrub, reflink owner accounting, and correct tracking of metadata/file/COW extents.

## Important APIs, types, and functions
Exported low-level APIs include `xfs_rmap_lookup_le`, `xfs_rmap_lookup_eq`, `xfs_rmap_insert`, `xfs_rmap_get_rec`, `xfs_rmap_query_range`, `xfs_rmap_query_all`, `xfs_rmap_has_records`, `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`, and `xfs_rmap_map_raw`. Direct per-AG update wrappers are `xfs_rmap_alloc` and `xfs_rmap_free`.

Deferred high-level APIs include `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`, `xfs_rmap_alloc_extent`, `xfs_rmap_free_extent`, and `xfs_rmap_finish_one`. `struct xfs_rmap_intent` carries owner, fork, bmbt extent, group, realtime flag, and operation type. Owner constants such as `XFS_RMAP_OINFO_FS`, `XFS_RMAP_OINFO_REFC`, and `XFS_RMAP_OINFO_COW` provide canonical metadata owners.

Validation flows through `xfs_rmap_btrec_to_irec`, `xfs_rmap_check_irec`, and `xfs_rtrmap_check_irec`. The validators enforce legal block ranges, owner classes, offset/fork rules, unwritten restrictions, and realtime group constraints.

## Control flow
Mapping an extent unpacks owner info, chooses ordinary or shared behavior, searches for adjacent mergeable records, and either extends a left/right neighbor or inserts a new record. Unmapping finds the covering record, verifies owner and unwritten state unless the owner is unknown for EFI recovery, then deletes, trims, or splits the record. Conversion toggles the unwritten flag for a file data extent, using a state bitmask to decide whether to merge with left/right neighbors or split a previous record into up to three records.

Reflink-capable file data can overlap by physical block with different owners, so shared variants (`xfs_rmap_map_shared`, `xfs_rmap_unmap_shared`, `xfs_rmap_convert_shared`) use range queries plus delete/insert when key fields change. Non-overlapping metadata and ordinary mappings use simpler cursor-local updates. `__xfs_rmap_finish_intent` dispatches deferred operations to the correct implementation; `xfs_rmap_finish_one` creates or reuses an AG or RTG cursor, translates the bmbt startblock to group block number, applies the change, and calls live update hooks.

## State and persistence behavior
Persistent state is the AG or realtime reverse mapping btree. The record key is ordered by physical startblock, owner, and packed offset flags; unwritten is a record attribute that is masked out of key comparisons. Mutations happen inside transactions through generic btree update/insert/delete. Deferred rmap intents are allocated from `xfs_rmap_intent_cache` and logged by the rmap item layer. AG finishers refresh the freelist before changing the rmapbt because btree shape changes allocate from AGFL; RTG finishers lock/join the realtime group with `XFS_RTGLOCK_RMAP`.

## Dependencies and integration points
This file depends on btree operations, rmap btree cursor construction, realtime rmap btree cursors, transactions, allocation/free-list management, inode fork state, reflink feature detection, health marking, tracepoints, and optional live hooks. Bmap update paths enqueue file mapping changes; allocation code calls metadata map/free helpers; scrub/repair use range queries and owner-count helpers; refcount COW tracking calls rmap alloc/free with `XFS_RMAP_OWN_COW`.

## Risks and invariants
The most sensitive logic is interval trimming, logical offset adjustment, shared-overlap lookup, and key-field updates. Invariants include nonzero blockcount, valid owner IDs or metadata owner range, no offsets for non-inode owners, no unwritten metadata/attr/bmbt records, exact bmbt offset zero, and full coverage for unmap/convert operations. `XFS_RMAP_OWN_UNKNOWN` intentionally relaxes owner checks for log recovery; misuse outside recovery would hide mismatches.

## Test signals
Coverage should include metadata allocation/free, file map/unmap, unwritten conversion, reflink shared owner overlaps, EFI recovery unknown-owner frees, realtime rmap operations, live hook notification, and corruption paths that mark the btree sick. Scrub tests should validate `xfs_rmap_count_owners` and `xfs_rmap_has_other_keys` on shared and non-shareable owners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.h

## Purpose
`xfs_rmap.h` declares reverse mapping owner helpers, packed-offset helpers, low-level btree operations, deferred intent APIs, owner query APIs, and optional live update hook interfaces.

## Important APIs and types
`xfs_rmap_ino_owner` and `xfs_rmap_ino_bmbt_owner` construct `xfs_owner_info` for inode data/attr fork extents and bmbt blocks. `xfs_rmap_irec_offset_pack` and `xfs_rmap_irec_offset_unpack` encode/decode fork, bmbt, and unwritten flags into the high bits of the on-disk offset field; `xfs_owner_info_pack` and `xfs_owner_info_unpack` convert between owner-info and rmap flags.

The header declares direct update/query primitives, `enum xfs_rmap_intent_type`, `struct xfs_rmap_intent`, deferred enqueue functions for file and metadata changes, and the finisher `xfs_rmap_finish_one`. It also defines `struct xfs_rmap_matches` for owner-count analysis and `struct xfs_rmap_update_params` for live hook callbacks.

## Control flow and integration
Callers choose between direct AG operations (`xfs_rmap_alloc`, `xfs_rmap_free`) and deferred operations (`xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, conversion, metadata alloc/free). The finisher uses the encoded intent to update the persistent rmapbt. Scrub/repair callers use `xfs_rmap_query_range`, `xfs_rmap_query_all`, owner counting, and raw map insertion.

## State and persistence behavior
The header defines no persistent storage, but its packed offset format is part of the on-disk rmap record contract. `XFS_RMAP_OINFO_SKIP_UPDATE` uses owner `XFS_RMAP_OWN_NULL` to suppress owner updates; `XFS_RMAP_OINFO_ANY_OWNER` uses `XFS_RMAP_OWN_UNKNOWN` for wildcard-style recovery paths.

## Dependencies, risks, and test signals
The API depends on `xfs_btree_cur`, transactions, inodes, bmbt records, perag/rtgroup structures, and optional `CONFIG_XFS_LIVE_HOOKS`. Risks center on mismatched packed flag semantics and misuse of skip/unknown owner sentinels. Tests should cover owner-info round trips, deferred intent dispatch, hook enable/disable behavior, and rmap query callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.c

## Purpose
`xfs_rmap_btree.c` defines the per-AG reverse mapping btree geometry, verifier, cursor allocation, block allocation/free policy, in-memory btree variant for repair, reserve calculations, and staged commit support. The rmapbt is an overlapping btree ordered by physical block, owner, and offset, allowing multiple file owners for shared reflink blocks.

## Important APIs and functions
Exports include `xfs_rmapbt_init_cursor`, `xfs_rmapbt_commit_staged_btree`, `xfs_rmapbt_maxrecs`, `xfs_rmapbt_compute_maxlevels`, `xfs_rmapbt_calc_size`, `xfs_rmapbt_max_size`, `xfs_rmapbt_calc_reserves`, `xfs_rmapbt_maxlevels_ondisk`, cursor cache lifecycle, and when `CONFIG_XFS_BTREE_IN_MEM` is enabled, `xfs_rmapbt_mem_cursor` and `xfs_rmapbt_mem_init`.

The `xfs_rmapbt_ops` table sets `XFS_BTGEO_OVERLAPPING`, uses two keys per pointer, and supplies root/block/key/verify/ordering callbacks. The in-memory ops mirror the same key behavior but use long pointers and `xfbtree` allocation callbacks.

## Control flow
New rmapbt blocks are allocated from the AGFL via `xfs_alloc_get_freelist`, reused through the busy extent mechanism, counted in `agf_rmap_blocks`, and charged against the `XFS_AG_RESV_RMAPBT` reservation. Freed blocks return to the AGFL, are marked busy with skip-discard, and decrement the rmapbt reservation. Root changes update `agf_rmap_root` and `agf_rmap_level`; staged-tree commit replaces root/level/block count from a fake root and logs all relevant AGF fields.

Key initialization masks unwritten from key comparisons because unwritten is a record attribute, while attr fork and bmbt flags remain key-significant. High keys extend both startblock and, for normal file mappings, logical offset to the final block covered by the record.

## State and persistence behavior
Persistent AGF fields are `agf_rmap_root`, `agf_rmap_level`, and `agf_rmap_blocks`. The btree stores `xfs_rmap_rec` records and internal nodes with low/high key pairs for overlapping range support. Verifiers require rmapbt feature support, valid v5 AG btree headers, correct CRC, valid level bounds, and generic block layout consistency. In-memory rmap btrees use CRC-less verification and fsblock-style headers for repair staging.

## Dependencies and integration points
The implementation integrates with allocation freelists, AG reservations, busy extents, generic and in-memory btree frameworks, online repair staging, AG health, tracepoints, and mount geometry initialization. `xfs_rmap.c` uses these cursors for all normal rmapbt edits; repair uses the in-memory and staged variants.

## Risks and test signals
Risks include incorrect overlapping-key high key construction, treating unwritten as key-significant, AGFL/reservation imbalance, and maxlevel underestimation on highly shared reflink filesystems. Tests should cover maxlevel calculations with reflink on/off, verifier failures, AGFL exhaustion behavior, staged repair commit, in-memory btree creation, and ordering of records with identical startblock but different owners/offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.h

## Purpose
`xfs_rmap_btree.h` declares the reverse mapping btree block layout macros and cursor/geometry functions for on-disk and in-memory rmap btrees.

## Important APIs and layout
`XFS_RMAP_BLOCK_LEN` is the v5 short btree header length. `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, and `XFS_RMAP_PTR_ADDR` address records, low keys, high keys, and pointers in a block. The two-key-per-pointer layout reflects overlapping btree geometry. Public functions cover cursor creation, staged commit, max record counts, mount maxlevel computation, size/reserve calculation, cursor-cache lifecycle, and in-memory btree cursor/init helpers.

## Control flow and state
The header supports normal rmapbt mutation, mount-time geometry setup, online repair staging, and memory-backed rmap indexes. Persistent state remains rooted in AGF fields, while the macros define exact on-disk block offsets that kernel and userspace libxfs code must share.

## Dependencies, risks, and test signals
The declarations depend on generic btree, mount, transaction, perag, staged fake-root, and `xfbtree` types. Risks are layout drift and incorrect handling of overlapping high-key storage. Tests should validate block layout calculations, in-memory cursor availability under config gates, and staged-tree callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.c

## Purpose
`xfs_rtbitmap.c` implements realtime allocator bitmap and summary manipulation shared with userspace libxfs. It reads and verifies realtime metadata buffers, searches and mutates free/allocated realtime extent bits, updates summary counters, frees realtime extents, queries free ranges, computes bitmap/summary geometry, and initializes realtime bitmap/summary files during creation or growfs.

## Important APIs and functions
Buffer APIs are `xfs_rtbuf_cache_relse`, `xfs_rtbitmap_read_buf`, and `xfs_rtsummary_read_buf`. Search/check/mutation APIs include `xfs_rtfind_back`, `xfs_rtfind_forw`, `xfs_rtcheck_range`, `xfs_rtmodify_range`, `xfs_rtmodify_summary`, `xfs_rtget_summary`, and `xfs_rtfree_range`. Higher-level exported operations are `xfs_rtfree_extent`, `xfs_rtfree_blocks`, `xfs_rtalloc_query_range`, `xfs_rtalloc_query_all`, `xfs_rtalloc_extent_is_free`, geometry helpers, `xfs_rtfile_initialize_blocks`, `xfs_rtbitmap_create`, and `xfs_rtsummary_create`.

The file defines buffer ops for legacy rt metadata and rtgroup-aware bitmap/summary metadata. Rtgroup format adds a header with magic, owner inode, block address, LSN, UUID, and CRC.

## Control flow
Bitmap/summary access goes through `xfs_rtbuf_get`, which maps the hidden metadata inode block with `xfs_bmapi_read`, reads the backing device buffer, verifies type/owner, marks the transaction buffer type, and caches one bitmap and one summary buffer in `struct xfs_rtalloc_args`. Bit searches operate word-by-word with masks across metadata file blocks. `xfs_rtmodify_range` sets or clears bits and logs only changed word spans.

Freeing a range first marks bitmap bits free, then uses backward/forward searches to find the complete newly free extent. It decrements summary counters for split-off fragments that are no longer free extents and increments the counter for the combined free run. `xfs_rtfree_extent` wraps this in transaction/superblock updates and legacy bitmap inode sequence reset behavior; `xfs_rtfree_blocks` validates realtime-block alignment, converts to realtime extents, and for rtgroups records the freed range as busy.

Queries scan the bitmap for state transitions, invoke callbacks for free records, and release cached buffers at the end. Initialization allocates file blocks with metadata bmap writes, then zeroes or copies content one block per transaction, installing rtgroup headers when needed.

## State and persistence behavior
Persistent state lives in hidden realtime bitmap and summary inodes, the superblock free realtime extent counter, and optionally rtgroup metadata headers. Bitmap bits use 1 for free and 0 for allocated. Summary counters are indexed by `log2(extent length)` and bitmap block number. Mutations are transaction-logged at buffer byte ranges; creation/growfs paths log entire initialized buffers and inode core size changes.

## Dependencies and integration points
This file depends on xfs bmap, transactions, realtime group inodes, mount geometry, health marking, buffer verifiers, superblock accounting, busy extent tracking, and error tags. Allocation code uses the check/search/summary APIs; free-space scrub and reporting use query helpers; growfs and mkfs-style initialization use the create/initialize helpers.

## Risks and invariants
Risks include bitmap/summary counter mismatch, alignment mistakes converting realtime blocks to realtime extents, stale cached buffers after switching blocks, header verification differences between legacy and rtgroup formats, and partial-word mask errors. Invariants include valid bitmap/summary file block bounds, written metadata mappings, correct owner inode in rtgroup headers, no zoned mode for bitmap operations, and exclusive lock ownership on the bitmap inode during frees.

## Test signals
Useful tests include freeing aligned and misaligned realtime ranges, boundary ranges crossing bitmap blocks, summary counter updates for splitting/merging free runs, rtgroup CRC/header verification, legacy no-rtgroups behavior, query-all/query-range callback coverage, and growfs initialization of bitmap/summary file blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.h

## Purpose
`xfs_rtbitmap.h` declares realtime bitmap/summary helper types, geometry conversions, inline accessors for legacy and rtgroup formats, query callback contracts, and exported realtime free/query/create functions.

## Important APIs and types
`struct xfs_rtalloc_args` bundles the target rtgroup, mount, transaction, cached bitmap buffer, cached summary buffer, and their file offsets. Conversion helpers translate among realtime blocks, realtime extents, realtime group block numbers, file offsets, bitmap file blocks, bitmap words, and summary offsets. Accessors such as `xfs_rbmblock_wordptr`, `xfs_rtbitmap_getword`, `xfs_rtbitmap_setword`, `xfs_rsumblock_infoptr`, `xfs_suminfo_get`, and `xfs_suminfo_add` abstract endianness and header offsets for rtgroup versus legacy formats.

`struct xfs_rtalloc_rec` and `xfs_rtalloc_query_range_fn` define callback-based free-space iteration. Under `CONFIG_XFS_RT`, the header declares buffer reads, range checks, find/modify helpers, summary helpers, free operations, free-space queries, geometry calculations, file initialization, and bitmap/summary inode creation. Without realtime support, important operations return `-ENOSYS`.

## Control flow and integration
The inline conversions are used throughout realtime allocation, free, scrub, and growfs code. Callers prepare `xfs_rtalloc_args`, invoke bitmap or summary helpers, and must release cached buffers with `xfs_rtbuf_cache_relse`. `xfs_rtblock_ops` selects CRC/header-aware buffer ops for rtgroups and generic ops for legacy metadata.

## State and persistence behavior
The header defines how persistent bitmap and summary words are interpreted. Legacy format stores native words at the start of the buffer; rtgroup format skips `struct xfs_rtbuf_blkinfo` and stores big-endian words. Summary offsets are derived from summary level and bitmap block number, then translated to metadata file block and in-block word.

## Dependencies, risks, and test signals
The header depends on mount realtime geometry fields, rtgroup structures, buffer ops, transaction types, and config gating. Risks are conversion drift for power-of-two versus non-power-of-two realtime extent sizes, endianness mistakes, and incorrect rtgroup header offset handling. Tests should cover all conversion helpers, `CONFIG_XFS_RT` stubs, rtgroup and legacy word accessors, and summary offset calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.h -->
