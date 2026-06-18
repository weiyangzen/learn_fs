# Group Research: group_1103_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_refcou_3b2bb5927691

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.c

## Scope

Implements XFS refcount btree record manipulation for reflink shared extents and in-progress CoW staging extents. The file covers AG refcount btrees and realtime-group refcount btrees, deferred intent replay, shared-range discovery, CoW staging recovery, and generic query helpers.

## APIs And Entry Points

- Lookup/read/update primitives: `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_btrec_to_irec`, `xfs_refcount_check_irec`, `xfs_rtrefcount_check_irec`, `xfs_refcount_get_rec`, `xfs_refcount_insert`.
- Deferred operation finishers: `xfs_refcount_finish_one` for AG refcount updates and `xfs_rtrefcount_finish_one` for realtime-group refcount updates.
- Intent producers: `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`, `xfs_refcount_alloc_cow_extent`, `xfs_refcount_free_cow_extent`.
- Query/recovery helpers: `xfs_refcount_find_shared`, `xfs_refcount_recover_cow_leftovers`, `xfs_refcount_has_records`, `xfs_refcount_query_range`.
- Slab lifecycle: `xfs_refcount_intent_init_cache`, `xfs_refcount_intent_destroy_cache`.

## Data Model

- Refcount records are represented by `struct xfs_refcount_irec`: start block, block count, refcount, and domain.
- Domains distinguish normal shared extents from CoW staging extents. Shared records must have `rc_refcount >= 2`; CoW-domain records must have `rc_refcount == 1`.
- Gaps in the shared-domain refcount btree are interpreted as allocated extents with refcount 1 when the caller is adjusting a mapped file extent.
- CoW staging allocations are deliberately stored as refcount-1 records in a separate key domain so crash recovery can find and free orphaned CoW blocks.

## Control Flow

- Boundary preparation:
  - `xfs_refcount_split_extent` splits any record crossing the start or end of an adjustment range.
  - `xfs_refcount_find_left_extents` and `xfs_refcount_find_right_extents` locate adjacent shoulder records and synthesize refcount-1 records for gaps inside the target range.
- Merge phase:
  - `xfs_refc_want_merge_center`, `xfs_refc_want_merge_left`, and `xfs_refc_want_merge_right` decide whether the adjusted center range can merge with adjacent records without exceeding `XFS_REFC_LEN_MAX`.
  - `xfs_refcount_merge_extents` performs center, left, or right merges before modifying middle extents.
- Adjustment phase:
  - `xfs_refcount_adjust_extents` increments/decrements middle shared extents, inserts records for refcount-1 gaps that become shared, removes records that drop to refcount 1, and schedules frees when decrementing below 1.
  - `xfs_refcount_still_have_space` conservatively limits work per transaction so deferred processing can continue safely.
  - `xfs_refcount_continue_op` and `xfs_rtrefcount_continue_op` rewrite unfinished intents to start at the next unprocessed group block.
- CoW phase:
  - `xfs_refcount_adjust_cow` uses the same split/merge boundary machinery but then calls `xfs_refcount_adjust_cow_extents`, which requires exact non-overlap on allocation and exact matching record deletion on free.
  - `xfs_refcount_recover_cow_leftovers` scans CoW-domain records after mount, queues each orphan, and later frees both the refcount record and the underlying blocks.

## Dependencies

- Uses generic XFS btree APIs, refcount btree cursor ops, realtime refcount cursor ops, allocation/free deferred extent machinery, transaction reservation state, reverse-map updates for CoW staging, group/perag/rtgroup helpers, health marking, tracepoints, and error injection tags.
- Depends on `xfs_refcount_encode_startblock` from the header for domain-aware key encoding.
- Realtime support depends on `xfs_rtgroup_lock`, `xfs_rtgroup_trans_join`, `xfs_rtrefcountbt_init_cursor`, and realtime block conversion/verification helpers.

## Invariants And Risks

- Shared and CoW domains must not be merged together; the separate domain checks and COW flag encoding preserve this.
- Refcount records must never cross the range boundaries before middle adjustment; otherwise decrement/free logic can corrupt ownership accounting.
- `XFS_REFC_REFCOUNT_MAX` records are pinned at max and skipped during adjustment.
- Transaction continuation depends on accurate `ri_blockcount` reduction and startblock rewrite.
- CoW recovery intentionally uses an empty transaction for the scan phase to avoid refcountbt buffer lock deadlocks, then frees leftovers one transaction at a time.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.h

## Scope

Public interface for XFS refcount operations, refcount deferred intents, refcount record validation, query callbacks, and CoW staging helpers.

## APIs And Types

- Declares btree lookup/read APIs: `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_get_rec`, `xfs_refcount_insert`.
- Defines `xfs_refcount_encode_startblock`, which encodes the CoW-domain bit into the on-disk startblock key for non-shared domains.
- Defines `enum xfs_refcount_intent_type`: increase, decrease, allocate CoW, free CoW.
- Defines `struct xfs_refcount_intent`, carrying deferred op type, target group, start block, block count, and realtime flag.
- Defines `xfs_refcount_check_domain`, enforcing that CoW records have refcount 1 and shared records have refcount at least 2.
- Declares deferred finishers for normal and realtime refcount trees.
- Declares CoW staging APIs, shared-range discovery, CoW leftover recovery, record packing/query helpers, validation helpers, and slab-cache lifecycle.

## Notable Constants

- `XFS_REFCOUNT_ITEM_OVERHEAD` estimates log space consumed per refcount update when deciding whether to continue an operation in the current transaction.
- `XFS_REFCOUNT_INTENT_STRINGS` maps intent types to trace/log strings.

## Dependencies

- Exposes types from transactions, mounts, per-AG state, btree cursors, bmap extents, realtime groups, btree records, and XFS record-packing results.

## Invariants And Risks

- `xfs_refcount_encode_startblock` treats any domain that is not explicitly shared as CoW-like for low-level btree range queries. Callers must set domains deliberately.
- The header codifies the semantic split between shared extents and CoW staging records; callers that bypass `xfs_refcount_check_domain` can accept impossible records.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.c

## Scope

Implements the per-AG refcount btree cursor operations, buffer verification, btree geometry calculations, reserve accounting, staged-btree commit, and cursor slab cache lifecycle.

## APIs And Entry Points

- Cursor and staging: `xfs_refcountbt_init_cursor`, `xfs_refcountbt_commit_staged_btree`.
- Geometry/reservation: `xfs_refcountbt_maxrecs`, `xfs_refcountbt_maxlevels_ondisk`, `xfs_refcountbt_compute_maxlevels`, `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, `xfs_refcountbt_calc_reserves`.
- Cache lifecycle: `xfs_refcountbt_init_cur_cache`, `xfs_refcountbt_destroy_cur_cache`.
- Exposes `xfs_refcountbt_buf_ops` and `xfs_refcountbt_ops`.

## Btree Operations

- Root state lives in AGF fields `agf_refcount_root`, `agf_refcount_level`, and `agf_refcount_blocks`.
- New btree blocks are allocated as metadata near the refcount btree target block with `XFS_RMAP_OINFO_REFC` ownership and `XFS_AG_RESV_METADATA`.
- Freed btree blocks decrement AGF block counts and are released through delayed extent freeing with refcount-btree rmap owner info.
- Record keys use encoded startblock. High keys are computed as `startblock + blockcount - 1`.
- Ordering is non-overlapping by encoded startblock; records are in order when one record’s end is less than or equal to the next start.

## Verification

- `xfs_refcountbt_verify` checks magic, reflink feature enablement, v5 AG btree header validity, tree level bounds, and block record counts.
- Online repair can temporarily validate against the larger of the current level and repair level.
- Read verification checks CRC first; write verification validates structure and updates CRC.

## Dependencies

- Uses generic btree, btree staging, allocation, AGF logging, rmap owner info, mount geometry, perag cached AGF state, online repair state, tracepoints, and health reporting.
- Depends on `xfs_refcount_encode_startblock` to build on-disk records from cursor state.

## Invariants And Risks

- Refcount btrees only exist on reflink filesystems.
- AGF root/level/block counters and perag cached levels must stay synchronized.
- Reserve calculations subtract internal log space from AG size because permanent log blocks cannot back future btree growth.
- Staged commits atomically swap in fake-root state; old tree cleanup is the caller’s responsibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.h

## Scope

Header for refcount btree on-disk block layout accessors, cursor creation, geometry helpers, reserve calculations, staged-tree commits, and cursor cache lifecycle.

## APIs And Macros

- `XFS_REFCOUNT_BLOCK_LEN` defines the short-form CRC btree block header length.
- `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, and `XFS_REFCOUNT_PTR_ADDR` compute record, key, and pointer addresses inside refcount btree blocks.
- Declares `xfs_refcountbt_init_cursor`, `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`, `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, `xfs_refcountbt_calc_reserves`, `xfs_refcountbt_commit_staged_btree`, `xfs_refcountbt_maxlevels_ondisk`, and cursor cache lifecycle functions.

## Dependencies

- Forward-declares XFS buffers, btree cursors, mounts, perag structures, transactions, and btree fake-root staging structures.

## Invariants And Risks

- Address macros are part of the userspace-visible libxfs interface and must match the on-disk refcount btree format exactly.
- Pointer layout assumes one key per child pointer, unlike overlapping btrees that carry low and high keys.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.c

## Scope

Implements XFS reverse mapping record operations for per-AG and realtime reverse-map btrees. It handles map/unmap/convert operations, shared-reflink variants, owner validation, deferred intent replay, live update hooks, raw insertion, range queries, owner-count checks, and slab cache lifecycle.

## APIs And Entry Points

- Primitive operations: `xfs_rmap_lookup_le`, `xfs_rmap_lookup_eq`, `xfs_rmap_insert`, `xfs_rmap_get_rec`, `xfs_rmap_btrec_to_irec`, `xfs_rmap_check_irec`, `xfs_rtrmap_check_irec`.
- Public map/free wrappers: `xfs_rmap_alloc`, `xfs_rmap_free`.
- Deferred replay: `__xfs_rmap_finish_intent`, `xfs_rmap_finish_one`.
- Intent producers: `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`, `xfs_rmap_alloc_extent`, `xfs_rmap_free_extent`.
- Query helpers: `xfs_rmap_lookup_le_range`, `xfs_rmap_query_range`, `xfs_rmap_query_all`, `xfs_rmap_has_records`, `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`.
- Raw and comparison helpers: `xfs_rmap_map_raw`, `xfs_rmap_compare`.
- Live hook APIs under `CONFIG_XFS_LIVE_HOOKS`: enable/disable/add/delete/setup.
- Slab lifecycle: `xfs_rmap_intent_init_cache`, `xfs_rmap_intent_destroy_cache`.

## Data Model

- Reverse-map records are keyed by physical group block, owner, and packed offset/flags.
- File data rmaps can overlap on reflink filesystems because multiple owners can map the same physical blocks.
- Metadata rmaps and bmbt/attr/non-inode owners are non-shareable and use simpler non-overlapping map/unmap logic.
- Offset packing stores attr-fork, bmbt-block, and unwritten flags in high offset bits; unwritten status is treated as a record attribute for btree key purposes.

## Control Flow

- Validation:
  - AG records validate extent range, owner class, flags, bmbt offset rules, unwritten restrictions, and file offset ranges.
  - Realtime records reject bmbt/attr flags, validate RT metadata owners separately, and require valid rtgroup extents for inode-owned records.
- Mapping:
  - `xfs_rmap_map` handles non-overlapping insertion and merges with compatible left/right neighbors.
  - `xfs_rmap_map_shared` uses delete/insert style updates because adjacent records in an overlapping btree can belong to other owners.
- Unmapping:
  - `xfs_rmap_unmap` removes or trims exact, left, right, or middle portions of a non-overlapping record. It has special handling for growfs null-owner checks and unknown-owner EFI recovery.
  - `xfs_rmap_unmap_shared` performs equivalent operations for shareable file data using owner/offset-aware range lookup and delete/insert where key fields change.
- Conversion:
  - `xfs_rmap_convert` toggles unwritten state for non-overlapping extents and handles eight main combinations of left/right filling and contiguous merge state.
  - `xfs_rmap_convert_shared` performs the same logical transformation for overlapping reflink data records.
- Deferred replay:
  - `xfs_rmap_finish_one` reuses a cursor when intents target the same group, initializes AG or realtime cursors as needed, reconstructs owner info from intent state, calls `__xfs_rmap_finish_intent`, then emits live hooks.
- Owner analysis:
  - `xfs_rmap_count_owners` trims queried records to the comparison range and counts owner/non-owner/conflicting non-owner matches.
  - `xfs_rmap_has_other_keys` stops early when any non-owner match is found.

## Dependencies

- Uses generic btree APIs, rmap btree cursors, realtime rmap cursors, transactions, bmap extent records, owner-info helpers, perag/rtgroup group state, filesystem feature flags, tracepoints, health marking, error tags, and deferred rmap log item infrastructure.
- Live hooks depend on XFS hook infrastructure and static jump-label switches.

## Invariants And Risks

- Shared reflink data paths must use overlapping-aware lookup; using the simple non-overlapping path can update the wrong owner record.
- Owner, offset, fork, bmbt, and unwritten flags are part of corruption detection, not advisory metadata.
- Unknown-owner free exists for log recovery and deliberately weakens owner checks; other callers should not use it casually.
- Deferred cursor reuse assumes operations are sorted by group and that cursor group mismatches are detected before replay.
- Realtime and AG validation rules differ; record checkers must be selected from cursor type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.h

## Scope

Public reverse-map interface and inline helpers for owner-info construction, rmap offset packing/unpacking, deferred intent structures, query callbacks, owner-count reporting, live hook declarations, and well-known metadata owner constants.

## APIs And Types

- Owner helpers: `xfs_rmap_ino_bmbt_owner`, `xfs_rmap_ino_owner`, `xfs_rmap_should_skip_owner_update`, `xfs_owner_info_pack`, `xfs_owner_info_unpack`.
- Offset helpers: `xfs_rmap_irec_offset_pack`, `xfs_rmap_irec_offset_unpack`.
- Primitive declarations: `xfs_rmap_alloc`, `xfs_rmap_free`, lookups, insert, get-rec, range/all queries.
- Deferred intent model: `enum xfs_rmap_intent_type`, `XFS_RMAP_INTENT_STRINGS`, and `struct xfs_rmap_intent`.
- Bmap-driven update APIs: map, unmap, convert, alloc/free metadata extent, finish-one replay.
- Query/comparison APIs: `xfs_rmap_lookup_le_range`, `xfs_rmap_compare`, record conversion/checking, `xfs_rmap_has_records`, `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`, `xfs_rmap_map_raw`.
- Owner-count result type: `struct xfs_rmap_matches`.
- Live update hook structures and functions when configured.

## Constants

- Declares well-known `xfs_owner_info` constants for skip update, any owner, filesystem, log, AG, inode btree, inode chunk, refcount btree, and CoW owners.
- `XFS_RMAP_INTENT_STRINGS` names deferred rmap operations for tracing/logging.

## Dependencies

- Depends on XFS owner-info flags, rmap record format flags, btree cursor APIs, transactions, inode fork ids, bmap records, groups, realtime groups, and hook infrastructure.

## Invariants And Risks

- Offset packing masks with `XFS_RMAP_OFF_MASK`; unexpected high bits in on-disk offset fields are corruption.
- `xfs_rmap_should_skip_owner_update` treats null owner as a sentinel, not a real reverse-map owner.
- `xfs_owner_info_pack` intentionally preserves only attr-fork and bmbt-block flags; unwritten state is supplied separately by bmap state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.c

## Scope

Implements per-AG reverse-map btree cursor operations, overlapping btree key behavior, buffer verification, in-memory rmap btree support, staged root commit, geometry calculations, reservation accounting, and cursor cache lifecycle.

## APIs And Entry Points

- Cursor and staging: `xfs_rmapbt_init_cursor`, `xfs_rmapbt_commit_staged_btree`.
- Optional in-memory btree support: `xfs_rmapbt_mem_cursor`, `xfs_rmapbt_mem_init`.
- Geometry/reservation: `xfs_rmapbt_maxrecs`, `xfs_rmapbt_maxlevels_ondisk`, `xfs_rmapbt_compute_maxlevels`, `xfs_rmapbt_calc_size`, `xfs_rmapbt_max_size`, `xfs_rmapbt_calc_reserves`.
- Cache lifecycle: `xfs_rmapbt_init_cur_cache`, `xfs_rmapbt_destroy_cur_cache`.
- Exposes `xfs_rmapbt_buf_ops`, `xfs_rmapbt_ops`, and in-memory ops under `CONFIG_XFS_BTREE_IN_MEM`.

## Btree Operations

- Root state lives in AGF fields `agf_rmap_root`, `agf_rmap_level`, and `agf_rmap_blocks`.
- Btree blocks are allocated from the AGFL via `xfs_alloc_get_freelist`; freeing returns blocks to AGFL and marks them busy with discard skipped.
- Rmap btree geometry is overlapping: internal pointers carry low and high keys, so `key_len` is two rmap keys per pointer.
- Keys are ordered by startblock, owner, and offset key. The unwritten bit is masked out of key comparisons because it is a record attribute.
- High keys add `blockcount - 1` to physical startblock and, for file-data records, to logical offset.

## Verification

- `xfs_rmapbt_verify` checks magic, rmapbt feature enablement, v5 AG btree header fields, tree level bounds, and record counts.
- Online repair can validate against the larger of current and repair rmap levels.
- In-memory btrees use long pointers, filesystem-block headers, no CRC checking, and are allowed even when the on-disk rmap feature is not enabled.

## Geometry And Reservations

- Reflink filesystems compute maximum height based on possible extreme sharing, using available AG space rather than one record per AG block.
- Non-reflink filesystems compute height assuming one rmap record per AG block.
- Reserve calculation adds the larger of 1% of AG blocks or enough space for one block per rmap record, subtracting internal log blocks when the AG contains the log.

## Dependencies

- Uses generic and in-memory btree infrastructure, AGF logging, AG reservations, AGFL allocation/free, extent-busy tracking, perag cached AGF state, online repair state, buf verification, rmap offset packing helpers, and trace/error infrastructure.

## Invariants And Risks

- Rmapbt blocks come from AGFL, so freelist/refill ordering and rmapbt reservations are part of correctness.
- Unwritten must be ignored in key comparisons but preserved in records; mixing this up can make convert operations fail or duplicate keys.
- Overlapping btree high-key calculations must match query expectations for shared reflink data.
- Staged commit swaps only the root metadata; callers must clean up old blocks after commit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.h

## Scope

Header for reverse-map btree block layout, cursor creation, staged commits, geometry/reservation calculations, cursor cache lifecycle, and in-memory rmap btree helpers.

## APIs And Macros

- `XFS_RMAP_BLOCK_LEN` defines the short-form CRC btree block header length.
- `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, and `XFS_RMAP_PTR_ADDR` compute record, low-key, high-key, and pointer addresses.
- Declares `xfs_rmapbt_init_cursor`, `xfs_rmapbt_commit_staged_btree`, max-record/max-level functions, size/reserve functions, and cursor cache lifecycle.
- Declares `xfs_rmapbt_mem_cursor` and `xfs_rmapbt_mem_init` for in-memory reverse-map btrees.

## Dependencies

- Forward-declares buffers, cursors, mounts, staged btree fake roots, in-memory btree objects, transactions, perag structures, buftargs, and AG numbers through included type context.

## Invariants And Risks

- Rmap internal nodes store both low and high keys for each pointer; address macros reflect that doubled key area.
- Rmap btrees require CRC-enabled filesystem formats.
- In-memory cursor declarations are available from the header but implementation is conditional in the C file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.c

## Scope

Implements realtime bitmap and summary file buffer access, verification, bitmap scanning/modification, summary updates, realtime extent freeing, free-space queries, geometry calculations, and initialization helpers for realtime bitmap/summary inode blocks.

## APIs And Entry Points

- Buffer/cache helpers: `xfs_rtbuf_cache_relse`, `xfs_rtbitmap_read_buf`, `xfs_rtsummary_read_buf`.
- Bitmap scanning: `xfs_rtfind_back`, `xfs_rtfind_forw`, `xfs_rtcheck_range`.
- Bitmap/summary mutation: `xfs_rtmodify_range`, `xfs_rtmodify_summary`, `xfs_rtget_summary`, `xfs_rtfree_range`.
- Freeing: `xfs_rtfree_extent`, `xfs_rtfree_blocks`.
- Querying: `xfs_rtalloc_query_range`, `xfs_rtalloc_query_all`, `xfs_rtalloc_extent_is_free`.
- Geometry: `xfs_rtbitmap_rtx_per_rbmblock`, `xfs_rtbitmap_blockcount_len`, `xfs_rtbitmap_blockcount`, `xfs_rtsummary_blockcount`.
- Initialization: `xfs_rtfile_initialize_blocks`, `xfs_rtbitmap_create`, `xfs_rtsummary_create`.
- Buffer ops: `xfs_rtbuf_ops`, `xfs_rtbitmap_buf_ops`, `xfs_rtsummary_buf_ops`.

## Data Model

- The realtime bitmap tracks free/allocated realtime extents; bit value 1 means free and 0 means allocated.
- The realtime summary tracks counts of free extents by `log2(length)` and bitmap block number.
- With realtime groups enabled, bitmap and summary blocks contain `struct xfs_rtbuf_blkinfo` headers with magic, owner inode, block address, LSN, and metadata UUID.
- `struct xfs_rtalloc_args` caches one bitmap buffer and one summary buffer for repeated operations.

## Control Flow

- Buffer acquisition:
  - `xfs_rtbuf_get` maps bitmap/summary file blocks through `xfs_bmapi_read`, reads the underlying device buffer with the correct ops, verifies owner for rtgroup formats, and caches the buffer in `xfs_rtalloc_args`.
- Scanning:
  - `xfs_rtfind_back` scans backward from a start extent until bitmap state changes.
  - `xfs_rtfind_forw` scans forward from start to limit until bitmap state changes.
  - `xfs_rtcheck_range` verifies a full range is all free or all allocated and returns the first mismatch.
- Mutation:
  - `xfs_rtmodify_range` sets/clears bitmap bits across partial words, whole words, and block boundaries, logging modified word ranges.
  - `xfs_rtmodify_summary` updates a summary counter and maintains the rtgroup summary cache when present.
  - `xfs_rtfree_range` marks a range free, finds neighboring free runs, removes stale summary counts for split runs, and adds the merged free extent summary.
- Freeing:
  - `xfs_rtfree_extent` verifies the range is allocated in debug builds, frees it, updates superblock free extents, and preserves legacy pre-rtgroup bitmap sequence behavior.
  - `xfs_rtfree_blocks` validates block alignment to realtime extent size, frees by realtime extents, and marks busy rtgroup blocks for rtgroup filesystems.
- Initialization:
  - `xfs_rtfile_initialize_blocks` allocates file blocks for bitmap/summary inodes and initializes each block in its own transaction.
  - `xfs_rtfile_initialize_block` writes rtgroup metadata headers when needed and fills data from a source buffer or zeroes.

## Dependencies

- Uses transaction buffer APIs, bmap reads/writes, realtime allocation arguments, realtime group inode accessors, inode locking/logging, superblock accounting, metadata buffer verification, checksum/LSN validation, extent-busy tracking, error tags, health marking, and mount geometry fields.

## Invariants And Risks

- All block and length arguments to `xfs_rtfree_blocks` must be aligned to realtime extent size.
- Bitmap and summary caches must be released after operations to drop transaction buffer references.
- Summary updates must reflect merged free extents exactly, or allocator free-space discovery becomes incorrect.
- Rtgroup bitmap/summary buffers require owner, UUID, block address, magic, checksum, and LSN validation.
- Zoned realtime configurations return zero bitmap/summary block counts and reject bitmap queries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.h

## Scope

Header for realtime bitmap/summary allocation arguments, realtime block/extent conversion helpers, bitmap and summary word accessors, buffer ops selection, free-space query record types, and public realtime bitmap APIs.

## APIs And Types

- Defines `struct xfs_rtalloc_args`, carrying rtgroup, mount, transaction, cached bitmap/summary buffers, and their file offsets.
- Conversion helpers cover rt extent to rt block, rtgroup block to extent, block lengths to rt extent lengths, alignment/modulo checks, file offset rounding to rt extent size, bitmap block/word mapping, and bitmap block to rt extent conversion.
- Bitmap word helpers: `xfs_rbmblock_wordptr`, `xfs_rtbitmap_getword`, `xfs_rtbitmap_setword`.
- Summary helpers: `xfs_rtsumoffs`, `xfs_rtsumoffs_to_block`, `xfs_rtsumoffs_to_infoword`, `xfs_rsumblock_infoptr`, `xfs_suminfo_get`, `xfs_suminfo_add`.
- Buffer ops selection: `xfs_rtblock_ops`.
- Query model: `struct xfs_rtalloc_rec` and `xfs_rtalloc_query_range_fn`.
- Under `CONFIG_XFS_RT`, declares buffer, scan, mutate, free, query, geometry, initialization, and create APIs.
- Without `CONFIG_XFS_RT`, provides `-ENOSYS` stubs for selected APIs.

## Data Model

- Legacy realtime bitmap and summary blocks store native-endian raw words.
- Rtgroup-enabled filesystems store big-endian words after an rt buffer header.
- `m_rtxblklog >= 0` enables shift/mask fast paths for power-of-two realtime extent sizes; otherwise helpers use division/modulo by `sb_reextsize`.

## Dependencies

- Includes `xfs_rtgroup.h` and depends on mount group geometry, realtime superblock fields, raw bitmap/summary word unions, buffer ops declarations, transactions, realtime group inodes, and XFS integer typedefs.

## Invariants And Risks

- Conversion helpers often mask rt block numbers to the rtgroup block mask before deriving extent numbers or offsets.
- Rtgroup and legacy formats differ in endianness and header placement; callers must use the provided accessors instead of direct buffer casts.
- `xfs_rtblock_ops` must match the inode type and filesystem format so verification and checksumming are correct.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtbitmap.h -->