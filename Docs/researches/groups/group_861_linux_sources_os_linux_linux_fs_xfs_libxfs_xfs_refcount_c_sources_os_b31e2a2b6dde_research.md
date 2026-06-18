# Group Research: group_861_linux_sources_os_linux_linux_fs_xfs_libxfs_xfs_refcount_c_sources_os_b31e2a2b6dde

Scope verified against `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.c

Implements XFS refcount btree semantic operations for reflink/shared blocks and CoW staging records. It covers lookup, record validation, insertion/deletion/update, range refcount increase/decrease, CoW reservation tracking, crash recovery of leftover CoW reservations, and deferred refcount intent execution for both AG and realtime group refcount btrees.

Key responsibilities:
- Converts on-disk refcount records to in-core `xfs_refcount_irec`, including shared vs CoW domain decoding via `XFS_REFC_COWFLAG`.
- Validates refcount records against AG or rtgroup geometry, domain rules, length limits, and refcount limits.
- Performs normalized range updates by splitting records at adjustment boundaries, merging adjacent compatible records, then adjusting middle records.
- Treats holes in the shared refcount btree as implicit refcount-1 allocated extents during file extent updates.
- Deletes records when shared refcount drops to 1, schedules block frees when refcount drops to 0, and pins saturated `XFS_REFC_REFCOUNT_MAX` records.
- Tracks CoW staging extents as domain-COW records with refcount 1, distinct from shared records.
- Recovers orphaned CoW staging allocations after crashes by scanning domain-COW records, freeing their rmap entries and blocks.
- Implements deferred operation finishers: `xfs_refcount_finish_one` for AGs and `xfs_rtrefcount_finish_one` for rtgroups.

Important functions:
- `xfs_refcount_lookup_le/ge/eq`, `xfs_refcount_get_rec`, `xfs_refcount_insert`
- `xfs_refcount_split_extent`, `xfs_refcount_merge_extents`, `xfs_refcount_adjust_extents`, `xfs_refcount_adjust`
- `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`
- `xfs_refcount_alloc_cow_extent`, `xfs_refcount_free_cow_extent`
- `xfs_refcount_find_shared`
- `xfs_refcount_recover_cow_leftovers`
- `xfs_refcount_has_records`, `xfs_refcount_query_range`
- `xfs_refcount_intent_init_cache`, `xfs_refcount_intent_destroy_cache`

Design notes:
- The file is transaction-reservation aware; `xfs_refcount_still_have_space` limits per-transaction dirtying and supports continuation intents.
- AG and realtime paths share the same core adjust logic because both expose group-relative btree cursors.
- Refcount shape changes are tracked on the btree cursor to estimate metadata overhead.
- Corruption paths mark the btree sick and return `-EFSCORRUPTED`.

Dependencies:
- Generic btree layer, AG/rtgroup geometry, free-space deferred freeing, rmap updates for CoW staging, transaction logging, health tracking, and errortag injection.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.h

Public interface for refcount btree operations and deferred refcount intents.

Key contents:
- Declares lookup/get/insert helpers for refcount btree cursors.
- Defines `xfs_refcount_encode_startblock`, which folds the refcount domain into the startblock key using `XFS_REFC_COWFLAG`.
- Defines deferred intent types: increase, decrease, allocate CoW, free CoW.
- Defines `struct xfs_refcount_intent`, carrying group, operation type, startblock, block count, and realtime flag.
- Provides `xfs_refcount_check_domain`, enforcing that CoW records have refcount 1 and shared records have refcount at least 2.
- Exposes high-level APIs for file extent refcount changes, CoW staging changes, CoW recovery, shared-range search, record existence checks, and range queries.
- Defines `XFS_REFCOUNT_ITEM_OVERHEAD` for transaction-space estimation during deferred refcount work.
- Declares slab cache lifecycle for refcount intents.

Design notes:
- The header abstracts both regular AG refcount and realtime refcount users.
- Domain validation is intentionally inline because both verifier and mutation code need the same invariant.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.c

Implements the AG refcount btree integration with the generic XFS btree framework. This file handles cursor setup, AGF root fields, block allocation/freeing, key construction, verifier callbacks, max-level calculations, staged repair commit, and reservation sizing.

Key responsibilities:
- Defines `xfs_refcountbt_ops` for the generic btree layer.
- Allocates refcount btree blocks from metadata reservation space near the refcount btree area, using owner info `XFS_RMAP_OINFO_REFC`.
- Updates AGF fields: `agf_refcount_root`, `agf_refcount_level`, and `agf_refcount_blocks`.
- Builds low/high keys from records; the high key is `startblock + blockcount - 1`.
- Encodes refcount domain into record keys via `xfs_refcount_encode_startblock`.
- Verifies refcount btree blocks: magic, reflink feature, v5 AG block header, level bounds, and record capacity.
- Provides buffer ops `xfs_refcountbt_buf_ops`.
- Supports online repair staging through `xfs_refcountbt_commit_staged_btree`.
- Computes max records, max levels, max size, and AG reservation requirements.
- Manages the cursor slab cache.

Important functions:
- `xfs_refcountbt_init_cursor`
- `xfs_refcountbt_alloc_block`, `xfs_refcountbt_free_block`
- `xfs_refcountbt_verify`, read/write verifiers
- `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`
- `xfs_refcountbt_calc_reserves`
- `xfs_refcountbt_commit_staged_btree`

Design notes:
- This file is about btree mechanics, not refcount semantics; semantic mutations live in `xfs_refcount.c`.
- It refuses verification if reflink is not enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.h

Header for AG refcount btree layout and exported btree helpers.

Key contents:
- Defines `XFS_REFCOUNT_BLOCK_LEN` as the v5 short btree block header length.
- Provides address macros for records, keys, and pointers inside refcount btree blocks:
  `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, `XFS_REFCOUNT_PTR_ADDR`.
- Declares cursor initialization, max-record calculation, max-level computation, size/reserve helpers, staged btree commit, and cursor cache lifecycle.

Design notes:
- Address macros are kept for both kernel and userspace consumers.
- The header intentionally exposes only btree-structure helpers; record mutation semantics are in `xfs_refcount.h/.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.c

Implements XFS reverse mapping btree semantic operations. Reverse mappings record physical block ownership by owner and logical offset, supporting metadata ownership, file data, reflink-overlapping mappings, unwritten conversion, deferred rmap intents, realtime rmap support, live hooks, and owner-count queries.

Key responsibilities:
- Lookup, insert, delete, update, and validate rmap records.
- Convert on-disk records to `xfs_rmap_irec`, including packed offset/flag decoding.
- Validate AG rmaps and realtime rmaps with separate rules for metadata and inode owners.
- Map and unmap physical extents, coalescing adjacent records where possible.
- Split existing records when unmapping middle ranges.
- Convert written/unwritten state with extensive case handling for left/right fill and neighbor contiguity.
- Provides shared/reflink-safe variants using delete+insert when key fields may overlap with other owners.
- Implements optimized left-neighbor and overlapping range lookups.
- Provides live rmap update hooks under `CONFIG_XFS_LIVE_HOOKS`.
- Processes deferred rmap intents for AG and realtime groups.
- Schedules rmap updates from bmap operations and metadata allocation/free operations.
- Counts matching and nonmatching owners for a physical range, used by scrub/repair/refcount validation.

Important functions:
- `xfs_rmap_lookup_le`, `xfs_rmap_lookup_eq`, `xfs_rmap_lookup_le_range`
- `xfs_rmap_get_rec`, `xfs_rmap_btrec_to_irec`, `xfs_rmap_check_irec`, `xfs_rtrmap_check_irec`
- `xfs_rmap_map`, `xfs_rmap_unmap`, `xfs_rmap_convert`
- `xfs_rmap_map_shared`, `xfs_rmap_unmap_shared`, `xfs_rmap_convert_shared`
- `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`
- `xfs_rmap_alloc_extent`, `xfs_rmap_free_extent`
- `xfs_rmap_finish_one`, `__xfs_rmap_finish_intent`
- `xfs_rmap_query_range`, `xfs_rmap_query_all`
- `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`
- `xfs_rmap_map_raw`

Design notes:
- Non-inode owners and bmbt blocks ignore logical offsets for merge decisions.
- Reflink data mappings are shareable and can overlap physically, so shared variants avoid unsafe in-place key changes.
- Corruption handling consistently marks the relevant btree sick.
- Deferred intent cursor reuse avoids repeated AGF/rtgroup locking and reduces lock ordering problems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.h

Public interface and inline helpers for reverse mapping operations.

Key contents:
- Owner-info constructors for inode bmbt owners and inode data/attr fork owners.
- `xfs_rmap_should_skip_owner_update` sentinel check.
- Inline pack/unpack helpers for rmap offset fields, including attr fork, bmbt block, and unwritten flags.
- `xfs_owner_info_pack/unpack` bridging owner-info flags and rmap record flags.
- Declares direct rmap allocation/free APIs and lower-level lookup/insert/get/query functions.
- Defines deferred rmap intent types and `struct xfs_rmap_intent`.
- Declares bmap-driven APIs for map, unmap, convert, metadata alloc, and metadata free.
- Declares owner-count result structure `xfs_rmap_matches`.
- Declares constants for common metadata owners such as FS, log, AG, inode btree, inode chunks, refcount btree, and CoW.
- Exposes optional live hook setup and registration APIs.

Design notes:
- The packed offset format treats unwritten as a record attribute, while attr fork and bmbt are key-significant.
- The deferred intent structure stores a full bmap record plus owner/fork metadata so updates can be replayed later.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.c

Implements reverse mapping btree mechanics for the generic XFS btree framework, including AG on-disk rmapbt and optional in-memory rmap btrees.

Key responsibilities:
- Defines AG rmap btree ops `xfs_rmapbt_ops`.
- Maintains AGF root, level, and block count fields for the rmap btree.
- Allocates/free rmapbt blocks from/to the AGFL, with busy extent handling and AG reservation accounting.
- Constructs low and high keys from records for an overlapping btree.
- Orders keys by physical startblock, owner, and packed offset with unwritten masked out.
- Verifies rmap btree buffers: magic, feature bit, v5 AG header, level bounds, and max records.
- Declares buffer ops `xfs_rmapbt_buf_ops`.
- Marks the btree geometry as overlapping via `XFS_BTGEO_OVERLAPPING`.
- Supports in-memory rmap btrees under `CONFIG_XFS_BTREE_IN_MEM`, including separate mem ops, buffer verification, cursor creation, and init.
- Supports staged btree commit for online repair.
- Computes max records, max levels, max size, and reservation requirements.
- Manages the rmap cursor slab cache.

Important functions:
- `xfs_rmapbt_init_cursor`
- `xfs_rmapbt_alloc_block`, `xfs_rmapbt_free_block`
- `xfs_rmapbt_init_key_from_rec`, `xfs_rmapbt_init_high_key_from_rec`
- `xfs_rmapbt_cmp_key_with_cur`, `xfs_rmapbt_cmp_two_keys`
- `xfs_rmapbt_verify`, read/write verifiers
- `xfs_rmapbt_mem_cursor`, `xfs_rmapbt_mem_init`
- `xfs_rmapbt_commit_staged_btree`
- `xfs_rmapbt_compute_maxlevels`, `xfs_rmapbt_calc_reserves`

Design notes:
- Internal nodes use two keys per pointer because rmap is an overlapping btree.
- On reflink filesystems, max-level calculation accounts for high sharing, where many owners can map one physical block.
- Reservation asks for the larger of 1% of the AG or max btree size.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.h

Header for reverse mapping btree layout and exported btree helpers.

Key contents:
- Defines `XFS_RMAP_BLOCK_LEN` as the v5 short btree block header length.
- Provides address macros for records, low keys, high keys, and pointers:
  `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, `XFS_RMAP_PTR_ADDR`.
- Declares AG rmap cursor creation, staged commit, max-record/max-level calculations, size/reserve helpers, and cursor cache lifecycle.
- Declares optional in-memory rmap btree cursor/init functions.

Design notes:
- Rmap internal blocks store low and high keys per pointer due to overlapping physical ranges.
- Some macros are preserved for userspace tooling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.c

Implements realtime bitmap and summary file operations shared with userspace-facing XFS logic. It manages rt bitmap/summary buffer verification, cached buffer access, bit scanning/modification, summary counter updates, realtime extent freeing, free-space queries, geometry calculations, and bitmap/summary file initialization.

Key responsibilities:
- Verifies rtgroup bitmap/summary buffer headers, CRCs, UUIDs, LSNs, owner inode, and block number.
- Provides buffer ops for legacy rt buffers and rtgroup bitmap/summary buffers.
- Caches one bitmap and one summary buffer in `xfs_rtalloc_args`.
- Reads bitmap/summary blocks through the rtgroup inode bmap and transaction buffer APIs.
- Finds free/allocated extent boundaries backward and forward using word-level bitmap scans.
- Modifies summary counters and maintains the per-rtgroup summary cache.
- Sets/clears ranges of bitmap bits and logs the modified byte spans.
- Frees realtime extents by updating bitmap, adjacent free-extent summaries, and superblock free extent count.
- Validates allocation state in debug builds before freeing.
- Frees block-count based realtime ranges after alignment checks.
- Iterates free realtime extents over a range or entire rtgroup.
- Tests whether an rt extent range is free.
- Computes bitmap and summary file block counts, including rtgroup header overhead and zoned mode behavior.
- Allocates and initializes bitmap/summary file blocks for growfs.
- Initializes rtbitmap/rtsummary inode sizes.

Important functions:
- `xfs_rtbitmap_read_buf`, `xfs_rtsummary_read_buf`, `xfs_rtbuf_cache_relse`
- `xfs_rtfind_back`, `xfs_rtfind_forw`
- `xfs_rtmodify_summary`, `xfs_rtget_summary`
- `xfs_rtmodify_range`, `xfs_rtfree_range`
- `xfs_rtcheck_range`
- `xfs_rtfree_extent`, `xfs_rtfree_blocks`
- `xfs_rtalloc_query_range`, `xfs_rtalloc_query_all`
- `xfs_rtalloc_extent_is_free`
- `xfs_rtbitmap_rtx_per_rbmblock`, `xfs_rtbitmap_blockcount`, `xfs_rtsummary_blockcount`
- `xfs_rtfile_initialize_blocks`, `xfs_rtbitmap_create`, `xfs_rtsummary_create`

Design notes:
- In rtgroups, bitmap/summary blocks contain `xfs_rtbuf_blkinfo` headers and store words big-endian; legacy files use older native word layout.
- Zoned filesystems return zero bitmap/summary block counts and reject rt bitmap queries.
- Freeing all realtime blocks on pre-rtgroup filesystems resets the bitmap inode sequence marker behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.h

Header for realtime bitmap/summary geometry, word access, and public realtime allocator helpers.

Key contents:
- Defines `struct xfs_rtalloc_args`, bundling rtgroup, mount, transaction, cached bitmap/summary buffers, and cached offsets.
- Provides conversion helpers among realtime extents, realtime blocks, rtgroup-relative blocks, block lengths, and alignment offsets.
- Provides rounding helpers for file offsets and block counts to realtime extent size.
- Maps rt extent numbers to bitmap file block and word offsets.
- Provides word pointer/get/set helpers for bitmap words, handling rtgroup header/bigendian format vs legacy layout.
- Provides summary offset, block, info-word, pointer, get, and add helpers.
- Selects buffer ops with `xfs_rtblock_ops`.
- Defines `struct xfs_rtalloc_rec` and range-query callback type.
- Declares realtime bitmap/summary read, scan, modify, summary, free, query, geometry, initialization, and inode-create APIs under `CONFIG_XFS_RT`.
- Supplies `-ENOSYS` stubs or no-op fallbacks when realtime support is disabled.

Design notes:
- Most geometry helpers optimize power-of-two realtime extent sizes through `m_rtxblklog`, falling back to division/modulo otherwise.
- Header helpers centralize legacy vs rtgroup layout differences so `xfs_rtbitmap.c` can operate mostly on abstracted words and counters.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtbitmap.h -->