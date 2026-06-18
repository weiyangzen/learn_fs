# Group Research: group_1098_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_btree__43226ab6699c

Scope: `Docs/research_subset_a.md`; source tree `sources/os/linux/linux-stable` is included in subset A.

Files researched:
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.c`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.c`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.c`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_cksum.h`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.c

## Role in the repository

`xfs_btree.c` is the generic XFS btree engine. It implements shared cursor navigation, lookup, insert, update, delete, balancing, block verification, query iteration, block ownership changes, cursor cache lifecycle, and inode-rooted metadata btree block allocation helpers. Filesystem-specific btrees such as allocation, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount plug into this core through `struct xfs_btree_ops`.

The implementation supports three btree placement models:
- AG-rooted btrees with short AG block pointers.
- Inode-rooted btrees with long filesystem block pointers and an in-inode root block.
- In-memory xfile-backed btrees used by online repair, with long pseudo block pointers.

## Core abstractions and layout

The file treats every btree block as a `struct xfs_btree_block` header followed by either records for leaf blocks or key/pointer arrays for internal blocks. All record, key, and pointer indexing is one-based, which is reflected in helpers such as `xfs_btree_rec_addr`, `xfs_btree_key_addr`, and `xfs_btree_ptr_addr`.

Block layout and addressing are driven by:
- `xfs_btree_block_len`, which chooses short/long and CRC/non-CRC header length.
- `xfs_btree_rec_offset`, `xfs_btree_key_offset`, `xfs_btree_high_key_offset`, and `xfs_btree_ptr_offset`, which compute field offsets from the ops-provided key, pointer, and record sizes.
- `xfs_btree_get_block`, which returns either an inode-rooted in-fork root block or a buffer-backed block for the requested cursor level.

For overlapping interval btrees, internal nodes store low and high keys per pointer. `xfs_btree_get_leaf_keys`, `xfs_btree_get_node_keys`, `xfs_btree_high_key_from_key`, `__xfs_btree_updkeys`, and `xfs_btree_update_keys` maintain those low/high key summaries. Regular btrees only need parent key updates when the first entry in a child changes; overlapping btrees generally need broader high-key maintenance because the maximum high key can be anywhere in the child.

## Verification and corruption handling

The file contains shared verifiers for long, short, and memory-backed btree blocks:
- `__xfs_btree_check_lblock_hdr`, `__xfs_btree_check_fsblock`, `__xfs_btree_check_memblock`, and `__xfs_btree_check_agblock` validate header magic, level, record count, UUID, block address, padding, and sibling pointers.
- `__xfs_btree_check_block` dispatches verification by btree type.
- `xfs_btree_check_block` converts verifier failures or injected btree check errors into `-EFSCORRUPTED`, traces corrupt buffers, and marks the owning metadata sick.
- `__xfs_btree_check_ptr` and `xfs_btree_check_ptr` validate block pointers against the appropriate address space: in-memory xfile blocks, filesystem blocks, or AG blocks.
- `xfs_btree_check_block_owner` verifies CRC-format owner fields when the caller has enough cursor context to know the expected owner.

The public verifier helpers near the end of the file are used by per-btree buffer verifiers:
- `xfs_btree_fsblock_v5hdr_verify` checks long-format v5 UUID, block number, and optional owner.
- `xfs_btree_fsblock_verify` checks long-format record count and filesystem-block siblings.
- `xfs_btree_memblock_verify` checks xfile-backed record count and xfile sibling pointers.
- `xfs_btree_agblock_v5hdr_verify` checks short-format v5 UUID, block number, and AG owner.
- `xfs_btree_agblock_verify` checks short-format record count and AG-block siblings.

CRC support is split by pointer format:
- `xfs_btree_fsblock_calc_crc` and `xfs_btree_fsblock_verify_crc` handle long-format blocks.
- `xfs_btree_agblock_calc_crc` and `xfs_btree_agblock_verify_crc` handle short-format blocks.

These functions update or validate the LSN and checksum only on CRC-enabled filesystems.

## Cursor lifetime and buffer handling

`xfs_btree_del_cursor` releases buffers attached to each cursor level, drops any held allocation group or realtime group reference, asserts that bmap cursors did not leak unaccounted allocations, and frees the cursor from its cache.

`xfs_btree_dup_cursor` duplicates a cursor by invoking the btree-specific `dup_cursor` callback, copying the current record and per-level cursor state, and re-reading all buffers attached to the source cursor. Staging cursors cannot be duplicated because they are private rebuild cursors. Metadata read failures that indicate sick metadata mark the duplicate cursor sick before unwinding.

`xfs_btree_setbuf` swaps the buffer for a cursor level, releases any previous buffer, resets sibling readahead state, and pre-marks missing left or right siblings as already read-ahead. `xfs_btree_buftarg` and `xfs_btree_bbsize` abstract the target and block size for disk-backed versus memory-backed btrees.

## Block initialization, logging, and primitive moves

`__xfs_btree_init_block`, `xfs_btree_init_block`, `xfs_btree_init_buf`, and `xfs_btree_init_block_cur` initialize btree headers with magic, level, record count, null sibling pointers, owner, UUID, LSN, block number, and buffer ops as appropriate.

The file centralizes transaction logging ranges:
- `xfs_btree_log_keys`, `xfs_btree_log_recs`, and `xfs_btree_log_ptrs` log changed key, record, and pointer ranges.
- `xfs_btree_log_block` logs selected header fields using offset tables for short and long formats. It deliberately avoids logging the CRC field directly because log recovery recreates block checksums.

Low-level movement helpers copy or shift keys, records, and pointers with the sizes supplied by `xfs_btree_ops`. These are used by balancing, splits, joins, insertion, deletion, and bulk root promotion/demotion.

## Lookup and navigation

`xfs_btree_lookup` performs a root-to-leaf binary search using `cmp_key_with_cur`. It handles empty single-leaf trees, exact/equal/less-or-equal/greater-or-equal lookup modes, and cursor positioning after off-block searches. Internal node descent is mediated by `xfs_btree_lookup_get_block`, which reuses a level buffer when possible, reads buffers otherwise, checks owners, verifies expected level, rejects empty internal nodes, and attaches the buffer to the cursor.

`xfs_btree_increment` and `xfs_btree_decrement` move a cursor forward or backward at a given level. They handle movement within the current block, crossing sibling blocks, walking upward to find the next/previous parent pointer, then walking back down to reset lower-level buffers and pointers. The functions issue directional readahead through `xfs_btree_readahead`.

`xfs_btree_goto_left_edge` positions a cursor before the first record by looking up the zero key and then decrementing, validating that the cursor did not land on a real record.

`xfs_btree_has_more_records` tests whether the current leaf has remaining records or a right sibling.

## Insert path

Insertion starts in `xfs_btree_insert`, which builds a leaf record and key from the cursor via btree-specific callbacks, then repeatedly calls `xfs_btree_insrec` from leaf toward root until no split pointer remains.

`xfs_btree_insrec`:
- Rejects insertion when the cursor points off the left edge.
- Checks ordering in debug builds.
- Calls `xfs_btree_make_block_unfull` if the target block is full.
- Inserts either a leaf record or an internal key/pointer by shifting entries right.
- Logs modified records, keys, pointers, and record counts.
- Updates parent keys when needed.
- Propagates split key/pointer state and a replacement cursor upward.

`xfs_btree_make_block_unfull` first tries right shift, then left shift, then split. For an inode-rooted in-fork root, it either expands the in-memory root with `broot_realloc` or promotes it into a real block with `xfs_btree_new_iroot`.

`__xfs_btree_split` allocates a right block, splits entries between old and new blocks, copies leaf records or internal key/pointer pairs, fixes sibling links, updates the right-right sibling if present, updates high keys for overlapping btrees, and returns the new block pointer/key. Kernel builds may route bmap btree splits through `xfs_btree_split_worker` to gain stack space while preserving transaction and reclaim context.

Root growth is split by root type:
- `xfs_btree_new_iroot` promotes an inode fork root into a real child block, handling both leaf roots and node roots.
- `xfs_btree_new_root` allocates a new external root for AG-rooted, memory-rooted, or staged AG btrees after root-level splits.
- `xfs_btree_set_root` updates either a staging fake root or the real btree-specific root callback.

## Update path

`xfs_btree_update` overwrites the current leaf record, logs it, and updates parent keys if the changed record can affect low/high key summaries. This path uses the same key propagation logic as insert/delete, which keeps standard and overlapping btrees consistent through one interface.

## Delete and rebalance path

`xfs_btree_delete` calls `xfs_btree_delrec` from leaf upward while joins require deleting parent key/pointer entries. If joins occurred in an overlapping tree, it force-updates high keys afterward.

`xfs_btree_delrec`:
- Removes a leaf record or internal key/pointer from the current block.
- Shrinks inode-rooted root blocks in memory.
- Collapses roots with a single child via `xfs_btree_kill_iroot` or `xfs_btree_kill_root`.
- Updates parent keys when the deleted entry affects key summaries.
- Accepts blocks that remain above minimum occupancy.
- Otherwise attempts to borrow from right or left siblings with `xfs_btree_lshift` or `xfs_btree_rshift`.
- Joins with a sibling when borrowing cannot fix underflow and combined records fit in one block.
- Fixes sibling pointers, frees the removed block, adjusts the cursor, and signals whether a parent entry must be removed.

Inode-rooted root demotion uses:
- `xfs_btree_demote_leaf_child` to copy child leaf records into the inode root.
- `xfs_btree_demote_node_child` to copy child node key/pointers into the inode root.
- `xfs_btree_kill_iroot` to replace a one-child inode root with the child contents when the child fits.

External-root collapse uses `xfs_btree_kill_root`, which updates the root pointer, frees the old root block, clears the old cursor level, and reduces tree height.

## Tree scanning, owner changes, and query helpers

`xfs_btree_visit_blocks` walks every block level left-to-right, optionally visiting internal and/or leaf levels. It uses sibling pointers and readahead, and `xfs_btree_visit_block` detects a self-referential right sibling to avoid cyclic traversal.

`xfs_btree_change_owner` uses `xfs_btree_visit_blocks` to rewrite owner fields throughout a CRC-format btree. When a transaction is present, it tries ordered buffer logging and can return `-EAGAIN` after logging a buffer normally if ordered logging was not possible. Without a transaction, it queues buffers for delayed write, which is useful in recovery-style contexts.

Range querying is implemented in two modes:
- `xfs_btree_simple_query_range` uses a less-or-equal lookup and forward iteration for non-overlapping btrees.
- `xfs_btree_overlapped_query_range` performs interval-tree-style traversal using low/high keys in internal nodes and leaf records.

`xfs_btree_query_range` converts caller-supplied incore low/high records to keys, validates ordering, and dispatches to the correct query mode. `xfs_btree_query_all` scans all records by using an all-zero low key and all-ones high key.

`xfs_btree_has_records` classifies a key range as empty, sparse, or full by iterating matching records and checking contiguity through the btree-specific `keys_contiguous` callback. It supports optional masked comparisons for use cases that intentionally ignore portions of the key.

`xfs_btree_count_blocks` counts all blocks by visiting the whole tree. `xfs_btree_cmp_two_ptrs` compares short or long btree pointers numerically.

## Size and height helpers

The file exposes generic geometry helpers:
- `xfs_btree_compute_maxlevels` computes the height needed for a number of records.
- `xfs_btree_calc_size` computes total btree blocks needed for a number of records.
- `xfs_btree_space_to_height` computes how tall a tree can be with a number of available leaf blocks.

These helpers are parameterized by leaf and node fanout limits.

## Cursor caches and metadata-file blocks

`xfs_btree_init_cur_caches` initializes cursor caches for allocbt, inobt, bmbt, rmapbt, refcountbt, realtime rmapbt, and realtime refcountbt, unwinding through `xfs_btree_destroy_cur_caches` on failure. `xfs_btree_destroy_cur_caches` destroys all those caches.

`xfs_btree_alloc_metafile_block` and `xfs_btree_free_metafile_block` allocate and free one block for inode-rooted metadata btrees. They require a metadata directory inode, use metadata-file AG reservation accounting, set rmap owner info for the inode/fork, and update metadata-file reserved space counters.

## Important invariants

- Btree block entries are one-based, not zero-based.
- Staging cursors cannot use normal allocation, freeing, duplication, query, or modification paths except through the staging bulk-loader interface.
- Inode-rooted btrees may have their root in the inode fork, so root-level functions must tolerate `bp == NULL`.
- Overlapping btrees require high-key maintenance after updates, shifts, splits, joins, and deletions.
- Internal nodes must not be empty; the code treats empty non-root internal blocks as corruption.
- CRC-format owner checks may be skipped for bmap extent-swap scenarios through `XFS_BTREE_BMBT_INVALID_OWNER`.
- Buffer logging for btree blocks records changed byte ranges but not checksum fields directly.

## Dependencies and callers

This file depends on XFS transaction, buffer, allocation, health, trace, rmap, metadata inode, xfile/memory buffer, and per-btree headers. Its exported functions are consumed by the concrete XFS btree implementations and by repair/scrub code that needs generic traversal, range queries, owner changes, and staging support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.h

## Role in the repository

`xfs_btree.h` declares the generic XFS btree interface, cursor structure, operation callback table, common key/record/pointer unions, traversal/query APIs, verification helpers, and utility inline functions used by all XFS btree implementations.

## Disk-format wrapper unions

The header defines generic wrappers around concrete btree formats:
- `union xfs_btree_ptr` stores either a short big-endian AG block pointer (`__be32 s`) or long big-endian filesystem/xfile block pointer (`__be64 l`).
- `union xfs_btree_key` contains key formats for bmap, allocation, inode allocation, rmap, and refcount btrees. It also reserves doubled rmap key storage for overlapping btrees.
- `union xfs_btree_rec` contains record formats for the same btree families.
- `union xfs_btree_irec` stores incore record representations for allocation, bmap, inode allocation, rmap, and refcount operations.

These unions let the core btree code copy and address opaque records while concrete btree implementations interpret contents.

## Operation table

`struct xfs_btree_ops` is the central contract between the generic engine and concrete btree types. It defines:
- The btree name, type, geometry flags, key/pointer/record sizes, LRU refs, stats offset, and health mask.
- Cursor duplication and optional cursor-state update callbacks.
- Root update callbacks.
- Block allocation/free callbacks.
- Minimum, maximum, and disk-root maximum record calculations.
- Callbacks to initialize keys, high keys, records, and root pointers.
- Key comparison, key ordering, record ordering, and contiguity callbacks.
- Buffer verifier ops.
- Optional inode-root reallocation callback.

The callback table is what allows one implementation in `xfs_btree.c` to drive AG btrees, inode btrees, realtime btrees, and memory-backed btrees.

## Geometry and type flags

`enum xfs_btree_type` distinguishes AG-rooted, inode-rooted, and in-memory btrees. The geometry flags are:
- `XFS_BTGEO_OVERLAPPING`, for interval btrees with low/high keys.
- `XFS_BTGEO_IROOT_RECORDS`, for inode-rooted btrees whose in-inode root can store records.

`enum xbtree_key_contig` and `xbtree_key_contig` classify numeric key fields as gap, contiguous, or overlapping. This supports range coverage checks and sparse/full classification.

## Cursor state

`struct xfs_btree_cur` stores all mutable traversal and mutation state:
- Transaction, mount, operation table, cursor cache, flags, current incore record, current height, maximum height, and optional group reference.
- Per-type state for inode-rooted, AG-rooted, and memory-backed btrees.
- Per-format private counters for bmap and refcount cursors.
- A flexible array of `struct xfs_btree_level` entries, one per tree level.

Each `xfs_btree_level` stores a buffer pointer, one-based key/record index, and sibling readahead flags.

Cursor flags include:
- `XFS_BTREE_STAGING`, meaning the cursor points to a fake root used by rebuild/bulk load.
- `XFS_BTREE_BMBT_WASDEL`, for bmap delalloc conversion.
- `XFS_BTREE_BMBT_INVALID_OWNER`, for extent swap owner-check suppression.
- `XFS_BTREE_ALLOCBT_ACTIVE`, for active allocation btree cursor state.

`xfs_btree_cur_sizeof` computes cursor allocation size for a given height. `xfs_btree_alloc_cursor` allocates a zeroed cursor from a kmem cache, stores common fields, and intentionally uses `__GFP_NOFAIL` because bmap allocations can arise in contexts where failure handling is not feasible.

## Public API surface

The header declares the main generic operations:
- Cursor lifecycle: `xfs_btree_del_cursor`, `xfs_btree_dup_cursor`.
- Navigation and search: `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`, `xfs_btree_goto_left_edge`.
- Mutation: `xfs_btree_update`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_new_iroot`.
- Record access: `xfs_btree_get_rec`.
- Query and traversal: `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_visit_blocks`, `xfs_btree_count_blocks`, `xfs_btree_has_records`, `xfs_btree_has_more_records`.
- Owner changes: `xfs_btree_change_owner`.
- Geometry calculations: `xfs_btree_compute_maxlevels`, `xfs_btree_calc_size`, `xfs_btree_space_to_height`.
- Buffer/block helpers: block verification, CRC helpers, block address helpers, sibling helpers, copy helpers, and initialization helpers.

The range query callback type `xfs_btree_query_range_fn` returns zero to continue and nonzero to stop. `-ECANCELED` is reserved as a clean early-stop value because the generic range query does not generate it by itself.

## Verification declarations

The header exposes block verifier helpers for:
- Long-format v5 headers and long-format btree blocks.
- Short-format v5 headers and short-format btree blocks.
- Memory-backed btree blocks.

It also exposes internal block and pointer checking helpers used by concrete btree verifiers and debug code.

## Inline helpers

Important inline helpers include:
- `xfs_btree_get_numrecs`, `xfs_btree_set_numrecs`, and `xfs_btree_get_level`.
- Key comparison wrappers around `cmp_two_keys`, including masked variants.
- `xfs_btree_islastblock`, which checks the right sibling pointer.
- `xfs_btree_at_iroot`, which identifies an inode-rooted in-fork root at the top level.

The header also declares shared metafile block allocation/free helpers for inode-rooted metadata btrees.

## Important invariants

- The core requires `ptr_len` to be either `XFS_BTREE_LONG_PTR_LEN` or `XFS_BTREE_SHORT_PTR_LEN`.
- Concrete btree code must supply callbacks that match its geometry and record format.
- Inode-rooted btrees need special handling because the root can be stored in an inode fork instead of a buffer.
- Overlapping btrees must provide high-key initialization and comparison semantics compatible with interval traversal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.c

## Role in the repository

`xfs_btree_mem.c` implements xfile-backed in-memory btree support. These btrees use the generic btree core with `XFS_BTREE_TYPE_MEM`, but their blocks live in an in-memory buffer target rather than on the filesystem device. This is primarily useful for online repair and rebuild workflows that construct temporary metadata indexes.

## Root and cursor callbacks

The file provides generic callbacks for memory btree operation tables:
- `xfbtree_set_root` updates the `struct xfbtree` root pointer and adjusts height by the supplied increment.
- `xfbtree_init_ptr_from_cur` copies the current memory btree root into a generic btree pointer.
- `xfbtree_dup_cursor` allocates a new generic cursor, copies common cursor state, shares the same `struct xfbtree`, and holds the cursor group reference if present.

These callbacks allow the generic code in `xfs_btree.c` to treat memory btrees like normal long-pointer btrees.

## Initialization and geometry

`xfbtree_init` initializes an empty memory btree:
- It requires a CRC-enabled filesystem.
- It requires long-format pointers.
- It stores the provided xfile buffer target.
- It computes leaf and node max/min records from `XMBUF_BLOCKSIZE`, the long CRC btree header length, and the concrete btree key/record sizes.
- It initializes height to one and creates an empty leaf root block through `xfbtree_init_leaf_block`.

`xfbtree_init_leaf_block` gets the first xfile-backed buffer, initializes it as a level-zero btree block with owner information, releases it, and records the root pointer.

`xfbtree_rec_bytes` returns the payload space available for records after the long CRC-format header. This is the basis for the max record calculations.

`xfbtree_destroy` drains the memory buffer target, releasing all resources associated with the xfile-backed btree.

## Allocation and free behavior

`xfbtree_alloc_block` allocates monotonically increasing pseudo block numbers from `xfbtree->highest_bno`. It verifies the block address fits the xfile buffer target with `xfbtree_verify_bno`; if not, it returns success with `stat = 0` so the generic btree core sees allocation failure without a direct errno.

`xfbtree_free_block` only decrements `highest_bno` when freeing the most recently allocated block. It does not maintain a free-space structure for arbitrary block reuse, which matches the temporary rebuild use case.

`xfbtree_get_minrecs` and `xfbtree_get_maxrecs` return the precomputed leaf or node fanout, selecting `maxrecs[0]/minrecs[0]` for leaves and `maxrecs[1]/minrecs[1]` for internal levels.

## Transaction commit and cancel handling

Memory btrees use regular transaction attachment to collect buffer pointers and avoid deadlocks, but their buffers must not commit through the normal filesystem log because the btree is temporary.

`xfbtree_buf_match` identifies transaction log items that are buffer log items for the memory btree's buffer target.

`xfbtree_trans_commit` walks transaction items:
- Non-xfbtree dirty items are remembered so the transaction dirty flag can be restored correctly.
- Xfbtree buffers are detached from the transaction.
- Each detached buffer is finalized immediately through `xmbuf_finalize`.
- Buffers are released even if verification/finalization reports an error.
- The transaction dirty bit is reset according to remaining non-xfbtree dirty items.

`xfbtree_trans_cancel` similarly detaches and releases xfbtree buffers without undoing changes. Its comment makes the lifetime requirement explicit: callers must not access the btree again after canceling changes this way.

## Important invariants

- Memory btrees require CRC format and long pointers.
- Blocks are addressed by `xfbno_t` values converted to/from disk addresses with the helpers in `xfs_btree_mem.h`.
- Memory btree allocation is append-style with only top-of-stack free rollback.
- Transaction commit/cancel paths remove all ephemeral btree buffers from the transaction so they do not enter the normal metadata log.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.h

## Role in the repository

`xfs_btree_mem.h` declares the in-memory xfile-backed btree interface used by online repair and other temporary btree users. It provides the address type, address conversion helpers, the `struct xfbtree` header, and function declarations enabled by `CONFIG_XFS_BTREE_IN_MEM`.

## Addressing model

The file defines:
- `xfbno_t` as a 64-bit xfile btree block number.
- `XFBNO_BLOCKSIZE` as `XMBUF_BLOCKSIZE`.
- `XFBNO_BBSHIFT` and `XFBNO_BBSIZE` for conversion between xfile btree blocks and 512-byte basic block units.
- `xfbno_to_daddr` and `xfs_daddr_to_xfbno` to convert between `xfbno_t` and `xfs_daddr_t`.

This lets the generic buffer and btree code address xfile-backed blocks through the same disk-address shaped APIs used for real metadata buffers.

## `struct xfbtree`

`struct xfbtree` stores the persistent in-memory btree header:
- The buffer cache target backing the xfile.
- The highest block number allocated so far.
- The owner value written into btree blocks.
- The generic root pointer and number of levels.
- Leaf and node min/max record counts.

The structure is intentionally small; the actual btree blocks live in the xfile buffer target.

## Conditional API

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, the header declares:
- Block verification: `xfbtree_verify_bno`.
- Generic btree callbacks: `xfbtree_set_root`, `xfbtree_init_ptr_from_cur`, `xfbtree_dup_cursor`.
- Fanout callbacks: `xfbtree_get_minrecs`, `xfbtree_get_maxrecs`.
- Block allocation/free callbacks: `xfbtree_alloc_block`, `xfbtree_free_block`.
- Lifecycle: `xfbtree_init`, `xfbtree_destroy`.
- Transaction detachment: `xfbtree_trans_commit`, `xfbtree_trans_cancel`.

When the option is disabled, `xfbtree_verify_bno` is defined as false, preventing accidental successful verification of memory btree addresses.

## Important invariants

- Callers must provide a buffer target and owner before initialization.
- Memory btree users must match the generic btree op table to long-pointer CRC btree semantics.
- The address conversion helpers assume xfile block sizes are powers compatible with basic block addressing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.c

## Role in the repository

`xfs_btree_staging.c` implements fake-root staging cursors and the generic bulk loader for constructing replacement XFS btrees. It is used by rebuild workflows, especially online repair, where a new btree must be built privately and then committed atomically by swapping the root into the live filesystem metadata.

The file deliberately separates staged construction from normal btree mutation. Regular btree operations are not supported on staging cursors; callers feed sorted records to the bulk loader and then commit the fake root through type-specific code.

## Staging cursor lifecycle

For AG-rooted btrees:
- `xfs_btree_stage_afakeroot` attaches a zeroed `struct xbtree_afakeroot` to a cursor, copies its current height, requires no transaction, and sets `XFS_BTREE_STAGING`.
- `xfs_btree_commit_afakeroot` clears the fake root pointer, restores the real AG buffer pointer and transaction, and clears staging mode. The caller must log the root change before this call.

For inode-rooted btrees:
- `xfs_btree_stage_ifakeroot` attaches a `struct xbtree_ifakeroot`, sets the cursor height, sets the staging fork size and fork selector, requires no transaction, and sets staging mode.
- `xfs_btree_commit_ifakeroot` clears the fake root pointer, restores the real fork selector and transaction, and clears staging mode. The caller must log the root change before committing.

The staging functions assert that the cursor type matches the fake root kind and that the cursor is not already staging.

## Bulk-load model

The bulk-load interface builds a whole btree from sorted records:
1. Caller initializes a fake root and staging cursor.
2. Caller fills an `xfs_btree_bload` descriptor.
3. `xfs_btree_bload_compute_geometry` computes height and block count.
4. Caller preallocates all blocks and exposes them through `claim_block`.
5. `xfs_btree_bload` formats all blocks bottom-up.
6. Caller commits the staged root to live metadata.

Preallocating every block is essential: bulk loading avoids mid-build ENOSPC failures and can lay out the new tree compactly.

## Buffer handling during loading

`xfs_btree_bload_drop_buf` queues a newly formatted btree buffer for delayed write, marks it up to date, releases it, and optionally flushes the ordered buffer list when `max_dirty` is reached. This throttles dirty buffers during large rebuilds.

`xfs_btree_bload_prep_block` allocates and initializes the next block at a given level:
- For inode-rooted root levels, it allocates an in-core root block using the caller's `iroot_size` callback and does not claim a disk block.
- For normal blocks, it calls the caller's `claim_block`, gets a buffer, links the previous block's right sibling to the new block, drops the previous buffer, initializes the new block header, sets its left sibling, and returns the new pointer/buffer/block.

Sibling links are therefore built incrementally left-to-right.

## Loading leaves and nodes

`xfs_btree_bload_leaf` fills a leaf block by repeatedly calling the caller's `get_records` callback. The callback receives the cursor, destination index, block pointer, number of wanted records, and private data. It returns the number loaded or a negative errno.

`xfs_btree_bload_node` fills an internal block with key/pointer entries. For each child pointer:
- It reads the child block.
- It copies the child pointer into the node.
- It derives the child low/high key summary with `xfs_btree_get_keys`.
- It copies the key into the node.
- It advances to the child's right sibling.

This builds parent levels from the leftmost block of the lower level upward.

## Geometry computation

`xfs_btree_bload_ensure_slack` normalizes caller slack values. Negative slack means approximately 75 percent fill, computed halfway between minrecs and maxrecs. Slack is capped so block occupancy cannot underflow below minimum records.

`xfs_btree_bload_max_npb` computes the maximum records or key/pointers to install in a block at a level. It respects inode-root maximum records for the root and subtracts leaf or node slack for regular blocks.

`xfs_btree_bload_desired_npb` clamps desired occupancy to at least minrecs for non-root levels and at least one entry for root levels.

`xfs_btree_bload_level_geometry` computes:
- Average items per block for a level.
- Number of blocks in the level.
- Number of leftmost blocks that receive one extra item to distribute uneven division.

It starts from desired occupancy, uses integer division so occupancy stays above the desired/minimum level, and increments block count if any block would exceed the absolute maximum.

`xfs_btree_bload_compute_geometry` uses these helpers from leaves upward. For inode-rooted btrees, it repeatedly recalculates geometry because the in-inode root has different capacity from regular blocks. It excludes the inode root from `nr_blocks` because it does not consume a separate filesystem block.

## Bulk-load execution

`xfs_btree_bload` performs the actual build:
- Initializes the buffer list, cursor height, dirty counter, and null child/current pointers.
- Computes leaf geometry and fills each leaf block with sorted records.
- Records the leftmost leaf pointer as the starting child pointer for the first node level.
- Flushes the final leaf buffer.
- For each internal level, computes geometry, creates node blocks, loads key/pointer pairs from the lower level, records the leftmost node pointer, and flushes the final block for that level.
- Updates the fake root with root pointer, height, and block count.
- Submits all delayed-write buffers and fails if the buffer list is unexpectedly non-empty afterward.
- Cancels any remaining delayed-write buffers and releases the active buffer on exit.

For inode-rooted btrees, the root pointer is expected to be null because the root is stored in the fake inode fork; the fake root records levels and block count excluding the in-core root. For AG-rooted btrees, the fake root stores the AG block root pointer, height, and total blocks.

## Important invariants

- Bulk loading requires `XFS_BTREE_STAGING`.
- Records supplied by `get_records` must already be sorted in btree order.
- All disk blocks must be preallocated and claimable before loading begins.
- Normal staged cursor mutation paths are intentionally blocked elsewhere in the btree core.
- Inode-rooted btree geometry must account for the special capacity of the in-inode root.
- The delayed-write list must be empty after final submission.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.h

## Role in the repository

`xfs_btree_staging.h` declares the fake-root structures and bulk-load API used to build replacement XFS btrees outside the live metadata root. It is the public header for staging cursors implemented in `xfs_btree_staging.c`.

## Fake roots

`struct xbtree_afakeroot` represents an AG-rooted btree under construction:
- `af_root`: AG block number of the new root.
- `af_levels`: height of the staged tree.
- `af_blocks`: number of blocks used by the staged tree.

`struct xbtree_ifakeroot` represents an inode-rooted btree under construction:
- `if_fork`: fake inode fork that owns the staged in-core root.
- `if_blocks`: number of disk blocks used by the staged btree.
- `if_levels`: height of the staged tree.
- `if_fork_size`: bytes available for the fork in the inode.

The header declares stage and commit functions for both fake root types.

## Bulk-load callback types

The header defines three callbacks:
- `xfs_btree_bload_get_records_fn`: load sorted records into a leaf block by setting cursor state and using the concrete btree record initializer.
- `xfs_btree_bload_claim_block_fn`: claim a preallocated block and return it as a generic btree pointer.
- `xfs_btree_bload_iroot_size_fn`: compute the byte size needed for an inode-rooted in-core root block.

These callbacks keep the generic loader independent from concrete record formats and allocation strategies.

## `struct xfs_btree_bload`

`struct xfs_btree_bload` carries all state for geometry and execution:
- Required callbacks: `get_records`, `claim_block`, and optional inode-root `iroot_size`.
- Input count: `nr_records`.
- Slack controls: `leaf_slack` and `node_slack`; negative values request automatic approximately 75 percent fill.
- Computed geometry: `nr_blocks` and `btree_height`.
- Dirty-buffer throttling: `max_dirty` and `nr_dirty`.

The public functions are:
- `xfs_btree_bload_compute_geometry`, which computes height and blocks for a planned record count.
- `xfs_btree_bload`, which formats and writes the staged tree.

## Important invariants

- Callers must use a staging cursor.
- Callers must preallocate every block reported by geometry before calling `xfs_btree_bload`.
- Inode-rooted callers must provide root sizing when the root can live in an inode fork.
- Slack controls affect regular btree blocks but are not enforced on inode root blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_cksum.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_cksum.h

## Role in the repository

`xfs_cksum.h` provides inline CRC32c checksum helpers for XFS metadata buffers that contain an embedded checksum field. Btree checksum helpers in `xfs_btree.c` ultimately rely on these buffer checksum primitives.

## Checksum algorithm

The checksum seed is `XFS_CRC_SEED`, defined as all ones in a 32-bit value.

`xfs_start_cksum_safe` verifies a buffer without modifying it. It computes CRC32c in three pieces:
- Bytes before the checksum field.
- A zero value in place of the checksum field.
- Bytes after the checksum field.

This allows verification while preserving the buffer contents.

`xfs_start_cksum_update` is the faster update path. It requires exclusive buffer access, writes zero into the checksum field, and computes CRC32c over the whole buffer in one pass.

`xfs_end_cksum` converts the intermediate CRC into on-disk format by complementing and storing it little-endian. The comment notes that CRC32c computation uses little-endian format even on big-endian machines, so byte swapping is required for consistent disk format.

## Public helpers

`xfs_update_cksum` updates a buffer in place:
- Zero checksum field.
- Compute CRC32c.
- Store the finalized little-endian checksum.

`xfs_verify_cksum` verifies a buffer:
- Compute the safe CRC with a logical zero checksum field.
- Compare the embedded little-endian checksum with the finalized expected value.

## Important invariants

- Update callers must have exclusive access because the checksum field is temporarily modified.
- Verification callers do not modify the buffer.
- The checksum field offset is supplied by the caller, which lets the same helpers serve btree blocks and other metadata formats with different checksum locations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_cksum.h -->