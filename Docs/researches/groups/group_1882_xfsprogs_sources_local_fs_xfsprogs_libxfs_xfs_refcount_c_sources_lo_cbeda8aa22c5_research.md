# Group Research: group_1882_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_refcount_c_sources_lo_cbeda8aa22c5

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/xfsprogs`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount.c

Implements XFS reflink reference count record operations for both AG refcount btrees and realtime refcount btrees. It manages shared-block refcounts, CoW staging extents, deferred refcount intents, record validation, range queries, and crash recovery of orphaned CoW allocations.

Core behavior:
- Provides lookup helpers `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, and `xfs_refcount_lookup_eq` over `(domain, startblock)`.
- Converts and validates on-disk refcount records with `xfs_refcount_btrec_to_irec`, `xfs_refcount_check_irec`, and `xfs_rtrefcount_check_irec`.
- Maintains strict domain semantics: shared records must have refcount >= 2; CoW staging records must have refcount exactly 1.
- Uses `xfs_refcount_insert`, internal update/delete helpers, and btree sickness marking on impossible cursor states or corrupt records.

Reference adjustment algorithm:
- `xfs_refcount_adjust` handles shared-domain increments/decrements.
- It first splits records crossing adjustment boundaries, then attempts left/right/center merges, then updates interior records.
- Gaps in the shared refcount btree are treated as implicit refcount-1 extents because allocated unshared blocks are not stored in refcountbt.
- Decrementing a record to refcount 1 deletes it from refcountbt; decrementing implicit or explicit refcount-1 space schedules block freeing.
- `xfs_refcount_still_have_space` conservatively limits how many record changes fit in the current transaction, allowing deferred continuations.

Deferred operation handling:
- `xfs_refcount_finish_one` processes AG refcount intents and reuses a refcountbt cursor while operations remain in the same AG.
- `xfs_rtrefcount_finish_one` performs the same operation for realtime groups, using rtgroup refcount locks and realtime block conversions.
- `__xfs_refcount_add`, `xfs_refcount_increase_extent`, and `xfs_refcount_decrease_extent` enqueue deferred refcount changes only when reflink is enabled.
- Continuation helpers update the intent startblock/blockcount after partial completion and verify the remaining range.

CoW staging support:
- CoW allocations are stored in the CoW refcount domain as refcount-1 records so that crash recovery can find allocated-but-unmapped CoW blocks.
- `xfs_refcount_alloc_cow_extent` records a CoW staging extent and creates an rmap owned by `XFS_RMAP_OWN_COW`.
- `xfs_refcount_free_cow_extent` removes the rmap and queues removal of the CoW refcount record.
- `xfs_refcount_recover_cow_leftovers` scans CoW-domain records at mount/recovery time, queues them for deletion, and frees the orphaned blocks.

Query and scan utilities:
- `xfs_refcount_find_shared` locates the first shared subrange in a physical extent and can optionally extend through contiguous shared records.
- `xfs_refcount_has_records` reports none/full/partial record coverage for a key range.
- `xfs_refcount_query_range` wraps generic btree range queries and validates each returned record.

Important interactions:
- Uses `xfs_refcount_btree.c` cursor and btree operations for AG refcountbt.
- Uses realtime refcount btree support through `xfs_rtrefcount_btree.h`.
- Calls rmap helpers to track CoW staging ownership.
- Calls deferred free helpers when refcount decreases release blocks.
- Marks AG/rtgroup btrees sick on corruption through btree health APIs.

Risk points:
- Boundary splitting, synthesized implicit refcount-1 records, and merge logic are correctness-critical.
- Shared and CoW domains share one encoded startblock namespace, so domain encoding/decoding must remain consistent.
- Transaction space estimation is intentionally conservative; wrong estimates can force continuation or risk reservation exhaustion.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount.h

Public interface for XFS refcount operations shared by libxfs users. It declares refcountbt lookup/query/update APIs, deferred intent types, CoW staging helpers, validation helpers, and cache lifecycle functions.

Key declarations:
- Lookup and read APIs: `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_get_rec`.
- `xfs_refcount_encode_startblock` stores the CoW-domain bit in the on-disk startblock key for non-shared domains.
- Intent enum values: increase, decrease, allocate CoW, free CoW.
- `struct xfs_refcount_intent` carries deferred operation type, group, startblock, blockcount, and realtime flag.
- Domain checker `xfs_refcount_check_domain` enforces CoW refcount 1 and shared refcount >= 2.

Exported workflows:
- `xfs_refcount_increase_extent` and `xfs_refcount_decrease_extent` enqueue file extent refcount adjustments.
- `xfs_refcount_finish_one` and `xfs_rtrefcount_finish_one` execute deferred AG or realtime refcount intents.
- `xfs_refcount_alloc_cow_extent`, `xfs_refcount_free_cow_extent`, and `xfs_refcount_recover_cow_leftovers` manage CoW staging records.
- `xfs_refcount_find_shared` supports shared-range discovery for reflink/COW decisions.
- `xfs_refcount_has_records` and `xfs_refcount_query_range` expose record coverage/query functionality.

Notable constants:
- `XFS_REFCOUNT_ITEM_OVERHEAD` is the conservative per-record transaction log space estimate used by the implementation.

Dependencies:
- Uses `struct xfs_btree_cur`, `struct xfs_bmbt_irec`, `struct xfs_refcount_irec`, `struct xfs_perag`, and `struct xfs_rtgroup`.
- Exposes `xfs_refcount_intent_cache` for deferred-item allocation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.c

Implements the AG-local refcount btree adapter for the generic XFS btree layer. It defines cursor allocation, block allocation/freeing, key/record conversion, verifier callbacks, btree ordering functions, staged repair commit, maxlevel calculation, and AG reservation sizing.

Btree behavior:
- `xfs_refcountbt_ops` defines a short-pointer AG btree named `refcount`.
- Records are ordered by encoded startblock, where the CoW flag is part of the key.
- Keys consist of a single refcount startblock; high keys are computed as `start + blockcount - 1`.
- Record initialization encodes the refcount domain through `xfs_refcount_encode_startblock`.

AG metadata integration:
- Root and level are stored in `agf_refcount_root` and `agf_refcount_level`.
- Block count is stored in `agf_refcount_blocks`.
- `xfs_refcountbt_set_root`, allocation, freeing, and staged commit log the relevant AGF fields.
- Refcountbt block allocations use metadata reservation and rmap owner `XFS_RMAP_OINFO_REFC`.

Verification:
- `xfs_refcountbt_verify` checks magic, reflink feature availability, v5 AG btree header validity, tree level limits, and block geometry.
- Read verification checks CRC first, then structure.
- Write verification validates structure and updates CRC.
- Online repair may temporarily validate against a repair tree level if configured.

Sizing and reservations:
- `xfs_refcountbt_maxrecs` computes leaf/internal record capacity after header overhead.
- `xfs_refcountbt_maxlevels_ondisk` computes an on-disk upper bound using minimum CRC block size.
- `xfs_refcountbt_compute_maxlevels` disables levels when reflink is absent.
- `xfs_refcountbt_calc_reserves` reads AGF state and asks for enough space for worst-case refcountbt growth, excluding internal log blocks.

Lifecycle:
- `xfs_refcountbt_init_cursor` allocates and initializes a cursor with AG buffer and perag group hold.
- `xfs_refcountbt_commit_staged_btree` installs a rebuilt staged btree root into AGF.
- `xfs_refcountbt_init_cur_cache` and destroy manage the cursor slab cache.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.h

Header for refcount btree on-disk block layout helpers and public btree management APIs.

Main contents:
- Defines `XFS_REFCOUNT_BLOCK_LEN` as the v5 short btree CRC header length.
- Provides address macros for records, keys, and pointers inside a refcount btree block:
  `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, `XFS_REFCOUNT_PTR_ADDR`.
- Declares cursor creation through `xfs_refcountbt_init_cursor`.
- Declares geometry helpers `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`, and `xfs_refcountbt_maxlevels_ondisk`.
- Declares sizing/reservation helpers `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, and `xfs_refcountbt_calc_reserves`.
- Declares staged btree commit and cursor cache lifecycle functions.

Role:
- This file exposes the btree adapter defined in `xfs_refcount_btree.c` to refcount update code, repair/build code, and userspace libxfs consumers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap.c

Implements reverse mapping record operations for XFS rmap btrees. It tracks physical extent ownership by owner, fork, offset, and flags; supports shared reflink-aware overlapping records; processes deferred rmap intents; exposes query/count helpers; and validates both AG and realtime rmap records.

Core record operations:
- `xfs_rmap_lookup_le` and `xfs_rmap_lookup_eq` search by physical block, owner, offset, and flags.
- `xfs_rmap_insert`, internal `xfs_rmap_delete`, and `xfs_rmap_update` mutate btree records.
- `xfs_rmap_btrec_to_irec` unpacks on-disk records, including offset flags.
- `xfs_rmap_check_irec` validates AG rmap records, including owner class, AG header special cases, file offsets, bmbt/attr/unwritten rules, and extent bounds.
- `xfs_rtrmap_check_irec` applies realtime-specific rules, allowing realtime filesystem metadata, CoW metadata when realtime reflink is enabled, and inode-owned data extents.

Mapping and unmapping:
- `xfs_rmap_map` handles non-overlapping rmap insertion and merges adjacent compatible records.
- `xfs_rmap_unmap` removes or splits records for freed/unmapped extents, with special handling for growfs null-owner extents and unknown-owner EFI recovery.
- `xfs_rmap_map_shared` and `xfs_rmap_unmap_shared` are overlap-aware variants for reflink file data; they use delete/insert when key fields change because neighboring records may belong to other owners.
- `xfs_rmap_map_raw` inserts a raw rmap, choosing shared or non-shared logic based on flags and owner class.

Conversion logic:
- `xfs_rmap_convert` toggles unwritten state for non-overlapping mappings.
- `xfs_rmap_convert_shared` performs the same operation for possibly overlapping reflink data records.
- Both conversion paths compute left/right adjacency and filling state, then update/delete/insert records to preserve btree order and maximize coalescing.

Deferred intents:
- `xfs_rmap_finish_one` processes deferred map, unmap, convert, alloc, and free operations, reusing a cursor while intents remain in the same group.
- `xfs_rmap_finish_init_cursor` refreshes AG freelist state before rmapbt updates.
- `xfs_rtrmap_finish_init_cursor` locks and joins realtime rmap state.
- Public enqueue helpers include `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`, `xfs_rmap_alloc_extent`, and `xfs_rmap_free_extent`.

Query and ownership analysis:
- `xfs_rmap_query_range` and `xfs_rmap_query_all` validate and pass rmap records to callbacks.
- `xfs_rmap_has_records` checks physical keyspace coverage.
- `xfs_rmap_count_owners` counts matching and nonmatching owners over a range.
- `xfs_rmap_has_other_keys` stops early when another owner overlaps the queried range.
- Shareability checks distinguish reflink-shareable file data from metadata or bmbt/attr records.

Live hook support:
- Under `CONFIG_XFS_LIVE_HOOKS`, rmap updates can notify registered hooks through a static switch.
- Hook APIs allow online fsck or similar users to monitor rmap updates with low inactive overhead.

Important interactions:
- Uses `xfs_rmap_btree.c` for AG rmapbt cursor/geometry.
- Uses realtime rmap btree support for rtgroup-backed records.
- Receives owner information from allocation, inode bmap, refcount CoW staging, and metadata allocation paths.
- Exposes owner constants such as `XFS_RMAP_OINFO_REFC`, `XFS_RMAP_OINFO_COW`, and `XFS_RMAP_OINFO_ANY_OWNER`.

Risk points:
- Offset flags are part key and part attribute: unwritten is ignored for key ordering, while attr fork and bmbt flags are key-significant.
- Shared rmap updates must not rely on adjacent cursor records belonging to the same owner.
- Unknown-owner recovery paths intentionally relax owner checks but still enforce range consistency.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap.h

Public interface for reverse mapping operations. It defines owner-info helpers, rmap offset packing, rmap intent types, query APIs, owner-match result structures, owner constants, and optional live hook declarations.

Key helpers:
- `xfs_rmap_ino_bmbt_owner` and `xfs_rmap_ino_owner` build owner-info records for inode bmbt and data/attr fork mappings.
- `xfs_rmap_should_skip_owner_update` tests for the null-owner sentinel.
- `xfs_rmap_irec_offset_pack` stores file offset plus attr fork, bmbt, and unwritten bits into the on-disk offset field.
- `xfs_rmap_irec_offset_unpack` validates and decodes that packed field.
- `xfs_owner_info_pack` and `xfs_owner_info_unpack` convert between owner-info flags and rmap flags.

Exported operations:
- Direct AG rmap APIs: `xfs_rmap_alloc`, `xfs_rmap_free`, lookups, insert, get record.
- Query APIs: `xfs_rmap_query_range`, `xfs_rmap_query_all`, `xfs_rmap_has_records`.
- Deferred update APIs from bmap/allocation paths: map, unmap, convert, alloc extent, free extent.
- Intent finish APIs: `xfs_rmap_finish_one` and `__xfs_rmap_finish_intent`.
- Validation and comparison: `xfs_rmap_btrec_to_irec`, AG/realtime record checks, `xfs_rmap_compare`.
- Ownership checks: `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`, and `struct xfs_rmap_matches`.

Intent model:
- `enum xfs_rmap_intent_type` distinguishes normal/shared map, normal/shared unmap, normal/shared conversion, metadata allocation, and metadata free.
- `struct xfs_rmap_intent` stores operation type, fork, owner, bmbt mapping, group, and realtime flag.

Constants:
- Declares common owner-info singletons for skip, any owner, filesystem, log, AG metadata, inode btrees, inode chunks, refcountbt, and CoW staging.

Optional hooks:
- Under `CONFIG_XFS_LIVE_HOOKS`, exposes hook setup/add/delete and enable/disable functions for rmap update observation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.c

Implements the AG reverse mapping btree adapter for the generic btree layer, plus optional in-memory rmap btree support. The rmap btree is an overlapping btree ordered by physical block, owner, and key-significant offset flags.

Btree model:
- `xfs_rmapbt_ops` defines an AG btree named `rmap` with `XFS_BTGEO_OVERLAPPING`.
- Internal nodes store low and high keys per pointer.
- Key ordering uses startblock, owner, and offset with the unwritten bit masked out.
- High-key construction extends both physical startblock and file offset for inode data/attr mappings; metadata and bmbt records do not advance offset.

AG integration:
- Root, level, and block count live in AGF fields `agf_rmap_root`, `agf_rmap_level`, and `agf_rmap_blocks`.
- Rmapbt blocks are allocated from the AGFL via `xfs_alloc_get_freelist`, not normal free-space allocation.
- Freeing returns blocks to AGFL and records busy extents with discard skipping.
- Reservation accounting uses `XFS_AG_RESV_RMAPBT`.

Verification:
- `xfs_rmapbt_verify` checks magic, rmapbt feature availability, v5 AG btree header, tree level limits, and block geometry.
- Read verification checks CRC then structure; write verification validates and updates CRC.
- Repair builds can temporarily validate against repair rmap levels.

In-memory rmap btree support:
- Under `CONFIG_XFS_BTREE_IN_MEM`, defines memory btree block capacity, verification, buffer ops, and `xfs_rmapbt_mem_ops`.
- `xfs_rmapbt_mem_cursor` creates cursors for in-memory rmap btrees.
- `xfs_rmapbt_mem_init` initializes an xfbtree with an AG owner.
- In-memory maxlevel calculation is folded into on-disk maxlevel bounds.

Sizing and reservations:
- `xfs_rmapbt_maxrecs` computes per-block record/key capacity.
- `xfs_rmapbt_maxlevels_ondisk` accounts for worst-case reflink sharing and optional in-memory tree height.
- `xfs_rmapbt_compute_maxlevels` uses space-to-height for reflink filesystems and one-record-per-block assumptions otherwise.
- `xfs_rmapbt_calc_reserves` reserves the larger of 1% of AG blocks or calculated max btree size, excluding internal log blocks.

Lifecycle:
- `xfs_rmapbt_init_cursor` creates AG cursors with perag group holds.
- `xfs_rmapbt_commit_staged_btree` installs staged repair roots into AGF.
- Cache lifecycle is handled by `xfs_rmapbt_init_cur_cache` and `xfs_rmapbt_destroy_cur_cache`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.h

Header for rmap btree layout macros and btree management declarations.

Main contents:
- Defines `XFS_RMAP_BLOCK_LEN` as the v5 short btree CRC header length.
- Provides block address macros for records, low keys, high keys, and pointers:
  `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, `XFS_RMAP_PTR_ADDR`.
- Declares AG cursor creation via `xfs_rmapbt_init_cursor`.
- Declares staged root commit, max record calculation, maxlevel computation, size calculation, max size, and reserve calculation helpers.
- Declares cursor cache lifecycle functions.
- Declares optional in-memory rmap btree cursor/init APIs through `xfs_rmapbt_mem_cursor` and `xfs_rmapbt_mem_init`.

Role:
- Exposes the overlapping rmap btree adapter to rmap update code, repair/staging code, and userspace libxfs consumers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.c

Implements realtime allocator bitmap and summary file operations shared with userspace. It verifies realtime bitmap/summary buffers, caches bitmap/summary reads, scans and modifies bitmap bits, updates summary counters, frees realtime extents, queries free realtime extents, computes realtime metadata geometry, and initializes realtime metadata files during grow/create.

Buffer verification and caching:
- `xfs_rtbuf_verify` validates rtgroup metadata headers: magic, rtgroups feature, CRC feature, metadata UUID, and block address.
- Read verification checks LSN and checksum before structural validation for rtgroup-enabled filesystems.
- Write verification updates LSN and checksum.
- Defines buffer ops for legacy rt buffers and rtgroup bitmap/summary buffers.
- `xfs_rtbuf_cache_relse` releases cached bitmap and summary buffers in `xfs_rtalloc_args`.
- `xfs_rtbuf_get` maps bitmap/summary inode file blocks to disk blocks, reads buffers, verifies rtgroup owner, tags buffer type, and caches the result.

Bitmap scanning:
- `xfs_rtfind_back` scans backward from a realtime extent until allocation/free state changes.
- `xfs_rtfind_forw` scans forward to a limit until allocation/free state changes.
- Both functions operate word-at-a-time with partial-word masks across bitmap blocks.
- `xfs_rtcheck_range` verifies that a range is all free or all allocated, returning the first mismatching extent.
- Debug-only `xfs_rtcheck_alloc_range` asserts that an extent is allocated before freeing.

Bitmap and summary modification:
- `xfs_rtmodify_range` sets a range of bitmap bits to free or allocated and logs modified word ranges.
- `xfs_rtmodify_summary` adjusts summary counters for a `(log2 extent size, bitmap block)` bucket and updates the per-rtgroup summary cache if present.
- `xfs_rtget_summary` reads a summary counter.
- `xfs_rtfree_range` marks realtime extents free, finds adjacent free extents, removes old summary records for neighboring fragments, and adds the merged free extent summary.

Freeing APIs:
- `xfs_rtfree_extent` frees an extent in realtime-extents units, updates the realtime bitmap/summary, increments superblock free extent count, and handles legacy all-free bitmap sequence reset behavior.
- `xfs_rtfree_blocks` accepts realtime block units, enforces realtime extent alignment, converts to rtextents, calls `xfs_rtfree_extent`, and marks rtgroup busy extents when rtgroups are enabled.

Free-space queries:
- `xfs_rtalloc_query_range` walks the bitmap over a requested extent range and invokes a callback for each free run.
- `xfs_rtalloc_query_all` scans all realtime extents in an rtgroup.
- `xfs_rtalloc_extent_is_free` checks whether a given extent is entirely free.

Geometry helpers:
- `xfs_rtbitmap_rtx_per_rbmblock` accounts for rtgroup headers reducing usable bitmap payload.
- `xfs_rtbitmap_blockcount_len` returns bitmap blocks needed for a number of realtime extents, with zoned filesystems returning zero.
- `xfs_rtbitmap_blockcount` and `xfs_rtsummary_blockcount` compute filesystem/rtgroup metadata file sizes and summary levels.

Metadata file initialization:
- `xfs_rtfile_alloc_blocks` allocates file blocks to bitmap or summary inodes.
- `xfs_rtfile_initialize_block` initializes one metadata block, writing rtgroup headers when enabled and copying or zeroing payload.
- `xfs_rtfile_initialize_blocks` allocates and initializes a file range one mapped extent at a time.
- `xfs_rtbitmap_create` and `xfs_rtsummary_create` set inode disk sizes and log inode core state.

Important interactions:
- Uses `xfs_rtbitmap.h` conversion and word access helpers.
- Uses bmap to map rt bitmap/summary inode blocks.
- Marks realtime metadata inodes sick on corrupt mappings or metadata buffers.
- Updates superblock free extent counters through transactions.
- Rejects bitmap query/free logic for zoned mode where appropriate.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.h

Header for realtime bitmap/summary helpers, conversion routines, free-space query types, and realtime allocator function declarations.

Core state:
- `struct xfs_rtalloc_args` carries rtgroup, mount, transaction, cached bitmap/summary buffers, and cached file offsets.

Realtime conversion helpers:
- Converts between realtime extent numbers, realtime block numbers, rtgroup block numbers, file block offsets, and lengths.
- Optimizes power-of-two realtime extent sizes through `m_rtxblklog`; otherwise uses division/modulo by `sb_rextsize`.
- Provides alignment helpers such as `xfs_extlen_to_rtxmod`, `xfs_blen_to_rtxoff`, `xfs_rtb_to_rtxoff`, and file offset rounding to realtime extent size.
- Handles rtgroup-relative masking for realtime block conversions.

Bitmap layout helpers:
- `xfs_rtx_to_rbmblock`, `xfs_rtx_to_rbmword`, and `xfs_rbmblock_to_rtx` map realtime extents to bitmap file locations.
- `xfs_rbmblock_wordptr` returns the correct bitmap word pointer, skipping rtgroup metadata headers when present.
- `xfs_rtbitmap_getword` and `xfs_rtbitmap_setword` abstract legacy native-endian words versus rtgroup big-endian words.

Summary layout helpers:
- `xfs_rtsumoffs` maps `(log2 length, bitmap block)` to summary word offset.
- `xfs_rtsumoffs_to_block` and `xfs_rtsumoffs_to_infoword` map summary offsets to file block and word positions.
- `xfs_rsumblock_infoptr`, `xfs_suminfo_get`, and `xfs_suminfo_add` abstract legacy and rtgroup summary word formats.

Buffer ops selection:
- `xfs_rtblock_ops` returns rtgroup-specific bitmap/summary buffer ops when rtgroups are enabled, otherwise legacy realtime buffer ops.

Query model:
- `struct xfs_rtalloc_rec` represents a free realtime extent run.
- `xfs_rtalloc_query_range_fn` is the callback signature for walking free realtime extents.

Declared APIs under `CONFIG_XFS_RT`:
- Buffer cache/read helpers for bitmap and summary files.
- Bitmap scanning/modification helpers: check range, find backward/forward, modify range.
- Summary get/modify helpers.
- Freeing APIs: `xfs_rtfree_range`, `xfs_rtfree_extent`, `xfs_rtfree_blocks`.
- Query APIs: range/all query and extent-is-free.
- Geometry APIs: bitmap extents per block, bitmap block counts, summary block count.
- Metadata initialization/create helpers for bitmap and summary files.

Fallback behavior:
- Without `CONFIG_XFS_RT`, most realtime APIs return `-ENOSYS` or zero-like stubs, allowing non-realtime builds to compile while rejecting runtime realtime operations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_rtbitmap.h -->