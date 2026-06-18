# Group Research: group_856_linux_sources_os_linux_linux_fs_xfs_libxfs_xfs_btree_c_sources_os_li_0f62dc9738b7

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.c

## Purpose

`xfs_btree.c` is the generic XFS btree core. It implements shared cursor traversal, lookup, insert, update, delete, block splitting/joining, root growth/shrink, validation, CRC helpers, query iteration, block visitation, ownership changes, cursor cache lifecycle, and generic block allocation helpers for inode-rooted metadata btrees.

This file is not a concrete btree type by itself. Concrete btrees such as allocbt, inobt, bmbt, rmapbt, refcountbt, realtime rmap/refcount btrees, and in-memory repair btrees provide `struct xfs_btree_ops` callbacks for key comparison, record encoding, allocation/freeing, root updates, and geometry. The core then performs all common structural operations.

## Btree Types Supported

The code dispatches on `cur->bc_ops->type`:

- `XFS_BTREE_TYPE_AG`: short-pointer btrees rooted in allocation group metadata, using AG block pointers.
- `XFS_BTREE_TYPE_INODE`: long-pointer btrees rooted in an inode fork, with the root possibly stored directly inside `if_broot`.
- `XFS_BTREE_TYPE_MEM`: long-pointer btrees backed by in-memory `xmbuf` buffer targets for online repair.

Pointer conversion, sibling verification, block target selection, block size selection, owner derivation, and root handling all branch on this type.

## Major Responsibilities

- Decode btree magic numbers from buffer verifier ops.
- Verify btree block headers, owner fields, sibling pointers, CRC metadata, and child pointers.
- Calculate CRCs for long-format and short-format btree blocks.
- Allocate, duplicate, and delete btree cursors.
- Calculate record, key, high-key, and pointer offsets inside btree blocks.
- Read, cache, release, and readahead btree buffers.
- Handle null pointer encoding for short and long pointer formats.
- Initialize btree blocks and buffers with correct owner, UUID, LSN, magic, level, and sibling fields.
- Log block headers, records, keys, and pointers into the current transaction.
- Traverse records forward and backward with `xfs_btree_increment` and `xfs_btree_decrement`.
- Lookup records with binary search at each level.
- Update records and propagate low/high key changes upward.
- Rebalance via left and right shifts.
- Split full blocks and create new roots.
- Insert records and propagate split pointers upward.
- Delete records, borrow from siblings, join blocks, and collapse roots.
- Visit all btree blocks level-by-level.
- Change btree block owner fields with ordered buffer logging.
- Run range queries for ordinary and overlapping-interval btrees.
- Classify a key range as empty, sparse, or fully packed.
- Compute btree height and block-count geometry from fanout limits.
- Initialize and destroy all btree cursor slab caches.
- Allocate/free blocks for inode-rooted metadata btrees.

## Key Data and Layout Model

The implementation treats btree blocks generically:

- Leaf blocks contain a common header followed by records.
- Internal blocks contain a common header followed by keys and then child pointers.
- Overlapping btrees store low and high keys for each pointer; high keys are addressed by offsetting halfway into the key storage area.

The helper family around `xfs_btree_block_len`, `xfs_btree_rec_offset`, `xfs_btree_key_offset`, `xfs_btree_high_key_offset`, and `xfs_btree_ptr_offset` centralizes this layout. Public address helpers expose typed pointers:

- `xfs_btree_rec_addr`
- `xfs_btree_key_addr`
- `xfs_btree_high_key_addr`
- `xfs_btree_ptr_addr`

All btree entry indexes are one-based, which is a core invariant throughout lookup, insert, delete, shifts, splits, and logging.

## Verification and Corruption Handling

The file contains layered verification:

- Header verification checks magic, level, `numrecs`, metadata UUID, block address, padding, and sibling pointers.
- Long-format filesystem-block siblings are validated as filesystem block numbers.
- Short-format AG-block siblings are validated against the current per-AG.
- In-memory siblings are validated against the `xmbuf` target.
- Child pointers are checked through `__xfs_btree_check_ptr`.
- Owner fields are verified during cursor-driven reads because not every buffer verifier has enough context.
- CRC verify helpers check v5 LSN and buffer checksum state before accepting CRC-format blocks.

Corruption reports mark the associated btree sick via `xfs_btree_mark_sick` and return `-EFSCORRUPTED`. Debug builds add extra pointer, order, and block checks along traversal and modification paths.

## Cursor Lifecycle

`xfs_btree_del_cursor` releases buffers held in `bc_levels`, drops any held group reference, checks bmap allocation accounting, and frees the cursor from its cache.

`xfs_btree_dup_cursor` clones cursor state and rereads every held buffer through the transaction. Staging cursors cannot be duplicated because staged rebuild state is intended to be private. Duplicated cursors are used heavily during sibling shifts and deletion rebalancing so parent paths can be updated without disturbing the primary cursor.

`xfs_btree_init_cur_caches` and `xfs_btree_destroy_cur_caches` initialize/destroy cursor caches for all concrete btree families.

## Lookup and Traversal

`xfs_btree_lookup` starts at the root, initializes a root pointer through `xfs_btree_init_ptr_from_cur`, reads each level with `xfs_btree_lookup_get_block`, binary-searches keys or synthesized leaf keys, and descends through the selected child pointer. It supports `XFS_LOOKUP_EQ`, `XFS_LOOKUP_LE`, and `XFS_LOOKUP_GE`, adjusting the final leaf cursor as needed.

`xfs_btree_increment` and `xfs_btree_decrement` advance a cursor at any level. If the movement stays within the current block, they only adjust the level pointer. If it crosses a block edge, they walk upward to find the next parent pointer and then walk back down, reading child blocks and resetting lower-level positions. They also issue sibling readahead.

`xfs_btree_goto_left_edge` positions the cursor before the first record by performing a low lookup and decrementing once.

## Key Propagation

The file maintains parent keys through:

- `xfs_btree_get_leaf_keys`
- `xfs_btree_get_node_keys`
- `xfs_btree_get_keys`
- `xfs_btree_update_keys`
- `xfs_btree_updkeys_force`

For ordinary btrees, parent keys usually need updating only when the first record/key of a block changes. For overlapping btrees, the highest key might be anywhere in the child subtree, so updates must recalculate and propagate both low and high key information more aggressively.

## Insert Path

`xfs_btree_insert` builds a record from the cursor through `init_rec_from_cur`, derives its key, and calls `xfs_btree_insrec` from the leaf upward until no split pointer remains.

Insertion behavior:

- If the target block has space, make a hole and copy in the new record or key/pointer.
- If the block is full, `xfs_btree_make_block_unfull` tries right shift, left shift, then split.
- If a split reaches the top of an AG/memory-rooted tree, `xfs_btree_new_root` creates a new root.
- If an inode-rooted root cannot grow inside the fork, `xfs_btree_new_iroot` promotes the inline root contents into a real block.
- Parent keys are updated unless the split result key must be propagated to the next level.

BMBT splits can be offloaded to a workqueue in kernel builds to avoid deep stack use, with care to avoid AGF/workqueue deadlocks.

## Delete Path

`xfs_btree_delete` calls `xfs_btree_delrec` from the leaf upward while joins require deleting parent key/pointer entries.

Deletion behavior:

- Remove a record or key/pointer by shifting later entries left.
- Shrink inode fork roots through `broot_realloc`.
- Collapse a root with one child through `xfs_btree_kill_root` or `xfs_btree_kill_iroot`.
- If a non-root block remains above minimum occupancy, finish.
- Otherwise try borrowing one entry from the right or left sibling.
- If borrowing cannot fix occupancy, join with a sibling, free the removed block, fix sibling links, and propagate deletion upward.
- For overlapping btrees, forced key updates are performed after joins.

The deletion path is careful about cursor consistency after joins, especially when the current block is merged into its left neighbor or when parent pointers must advance.

## Root Handling

The code has separate paths for externally rooted and inode-rooted trees:

- `xfs_btree_set_root` updates either the concrete btree root callback or a staging fake root.
- `xfs_btree_new_root` creates a new external root block after a root split.
- `xfs_btree_new_iroot` copies an inode root into a newly allocated real block when the inline root no longer fits.
- `xfs_btree_promote_leaf_iroot` and `xfs_btree_promote_node_iroot` convert inline root contents into child blocks.
- `xfs_btree_kill_iroot`, `xfs_btree_demote_leaf_child`, and `xfs_btree_demote_node_child` collapse inode-rooted btrees back into the fork when possible.

## Query and Scan Facilities

`xfs_btree_query_range` converts in-core low/high records to keys and dispatches:

- Ordinary btrees use `xfs_btree_simple_query_range`, which starts near the low key and walks forward until keys pass the high key.
- Overlapping btrees use `xfs_btree_overlapped_query_range`, which performs interval-tree-style descent using node low/high keys and invokes a callback for overlapping records.

`xfs_btree_query_all` scans the full keyspace.

`xfs_btree_has_records` classifies a key range as empty, sparse, or full by querying records and checking key contiguity. It detects illegal overlap for btrees that do not permit overlapping intervals.

`xfs_btree_has_more_records` checks whether the current leaf has more entries or a right sibling.

## Block Visitation and Owner Changes

`xfs_btree_visit_blocks` visits levels from root to leaves, walking each level left-to-right through sibling pointers. It can visit internal blocks, record blocks, or all blocks. It contains a loop-prevention check against a right sibling pointer referencing the current block.

`xfs_btree_change_owner` uses this walker to update owner fields in every block. With a transaction it uses ordered buffer logging and may ask the caller to roll via `-EAGAIN`; without a transaction it queues buffers for delayed write.

## Geometry Helpers

The file provides:

- `xfs_btree_compute_maxlevels`: height required for a record count.
- `xfs_btree_calc_size`: total blocks required for a record count.
- `xfs_btree_space_to_height`: height that can be supported by a given number of leaf blocks.

These are generic fanout calculations used by concrete btree setup and sizing code.

## Metadata Btree Block Helpers

`xfs_btree_alloc_metafile_block` and `xfs_btree_free_metafile_block` allocate/free blocks for inode-rooted metadata btrees. They integrate with metadata-directory inode checks, rmap owner setup, metafile reservation accounting, and deferred free handling.

## Integration Points

This file depends on:

- Concrete btree operation tables in XFS alloc, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount code.
- Transaction buffer read/get/log/release APIs.
- XFS buffer verifiers and CRC helpers.
- Per-AG/per-group references.
- Inode fork handling for inode-rooted btrees.
- Online repair staging and in-memory btree support.
- Health reporting through sick masks.
- Error-tag based fault injection.

## Important Invariants

- Cursor level arrays must match `bc_nlevels`.
- Entry indexes are one-based.
- Staging cursors must not use regular allocation/free/modification paths except bulk loading.
- Inode-rooted root blocks may have no buffer pointer.
- Non-root internal nodes must not be empty.
- Parent low/high keys must describe child subtree contents.
- Sibling pointers must not point to self and must reference valid blocks.
- Root collapse/growth must keep cursor height and root storage synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.h

## Purpose

`xfs_btree.h` declares the generic XFS btree interface, cursor structure, operation callbacks, common key/record/pointer unions, geometry flags, comparison helpers, traversal/query prototypes, verification prototypes, and cursor allocation helpers.

It is the contract between concrete XFS btree implementations and the generic engine in `xfs_btree.c`.

## Core Types

The file defines generic on-disk wrapper unions:

- `union xfs_btree_ptr`: short 32-bit AG pointers or long 64-bit pointers.
- `union xfs_btree_key`: key storage for bmbt, allocbt, inobt, rmapbt, refcountbt, and overlapping rmap high/low key storage.
- `union xfs_btree_rec`: record storage for the same btree families.
- `union xfs_btree_irec`: in-core record storage for generic query/update APIs.

The generic code treats these as opaque blobs whose size and interpretation are provided by `xfs_btree_ops`.

## `struct xfs_btree_ops`

`xfs_btree_ops` is the concrete btree vtable. It supplies:

- Name, type, geometry flags, key length, pointer length, record length, stats offset, health mask, and buffer verifier ops.
- Cursor duplication and optional cursor state update.
- Root pointer update callback.
- Block allocation/free callbacks.
- Minimum, maximum, and on-disk-root maximum record calculations.
- Record/key/pointer initialization callbacks.
- Key comparison callbacks against cursor state and against other keys.
- Key order, record order, and key-contiguity validators.
- Optional inode-root reallocation callback.

The generic engine depends on these callbacks for every type-specific decision.

## Geometry Flags

The header defines:

- `XFS_BTGEO_OVERLAPPING`: internal nodes store low/high keys for interval-overlap searches.
- `XFS_BTGEO_IROOT_RECORDS`: inode-rooted root blocks may directly store records.

These flags affect block layout, key propagation, root growth, bulk loading, range queries, and root conversion.

## Cursor Structure

`struct xfs_btree_cur` collects all state needed by generic btree operations:

- Current transaction and mount.
- Operation table and cursor cache.
- Feature flags.
- Current in-core record value.
- Current and maximum tree height.
- Optional group reference.
- Type-specific state for inode, AG, and in-memory btrees.
- Bmap/refcount private accounting fields.
- Per-level buffer pointer, entry pointer, and readahead state.

`bc_levels[]` is a flexible array and must be last. `xfs_btree_cur_sizeof` computes allocation size for a chosen height.

## Cursor Flags

Important flags include:

- `XFS_BTREE_STAGING`: cursor points at fake roots during rebuild/bulk load.
- `XFS_BTREE_BMBT_WASDEL`: bmap cursor is converting a delayed allocation reservation.
- `XFS_BTREE_BMBT_INVALID_OWNER`: skip bmap owner verification during extent swap.
- `XFS_BTREE_ALLOCBT_ACTIVE`: allocation btree cursor activity marker.

The generic code uses these flags to restrict staging operations, verify ownership, and preserve bmap-specific behavior.

## Public Operations

The header exposes generic btree APIs:

- Cursor lifecycle: `xfs_btree_del_cursor`, `xfs_btree_dup_cursor`, `xfs_btree_alloc_cursor`.
- Navigation: `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`, `xfs_btree_goto_left_edge`.
- Modification: `xfs_btree_update`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_new_iroot`.
- Record access: `xfs_btree_get_rec`.
- Block access: `xfs_btree_get_block`, `xfs_btree_lookup_get_block`, `xfs_btree_get_buf_block`, `xfs_btree_read_buf_block`.
- Layout access: record/key/high-key/pointer address helpers.
- Query/scan: `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_has_records`, `xfs_btree_has_more_records`.
- Block walking: `xfs_btree_visit_blocks`, `xfs_btree_count_blocks`, `xfs_btree_change_owner`.
- Sizing: `xfs_btree_compute_maxlevels`, `xfs_btree_calc_size`, `xfs_btree_space_to_height`.
- CRC and verifier helpers for short, long, and in-memory blocks.
- Metadata inode btree block allocation/free helpers.

## Inline Helpers

The header includes inline helpers for:

- Getting/setting `bb_numrecs`.
- Getting block level.
- Pointer null/equality support through declarations.
- Key comparison wrappers around `cmp_two_keys`.
- Masked key comparison wrappers.
- Determining if the cursor is on the last block at a level.
- Determining if a cursor level is the inode-root block via `xfs_btree_at_iroot`.
- Allocating a zeroed cursor from the concrete cursor cache.

## Query Contracts

`xfs_btree_query_range_fn` callbacks return zero to continue or nonzero to stop. `-ECANCELED` is explicitly documented as a normal stop-iteration signal because the query path does not generate it independently.

`xfs_btree_has_records` reports record packing through `enum xbtree_recpacking` and can accept a key mask for comparisons over only selected fields, used by callers such as reverse-mapping scans.

## Integration Points

Concrete btree code must include this header to create cursors, fill `xfs_btree_ops`, and invoke generic traversal/modification. Other XFS subsystems use the exported query and walk helpers to inspect or transform btrees without knowing the concrete block layout.

## Important Invariants

- `ops->ptr_len` must be either `XFS_BTREE_LONG_PTR_LEN` or `XFS_BTREE_SHORT_PTR_LEN`.
- `bc_levels[]` has exactly `bc_nlevels` active entries.
- Inode-root detection is based on btree type and top level.
- Operation callbacks must agree on key, pointer, record sizes and comparison semantics.
- Overlapping btrees must provide high-key initialization and proper key-contiguity behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.c

## Purpose

`xfs_btree_mem.c` implements the generic-btree adapter for in-memory XFS btrees backed by `xmbuf` buffer targets. These btrees are used by online repair and staging workflows that need btree semantics without committing intermediate state to filesystem metadata.

The file is compiled when in-memory btree support is enabled and provides root management, block allocation/freeing, geometry, cursor duplication, initialization, destruction, and special transaction commit/cancel handling.

## Main Responsibilities

- Store and update the in-memory btree root in `struct xfbtree`.
- Duplicate memory-btree cursors.
- Initialize an empty CRC-format long-pointer btree in an `xmbuf` target.
- Calculate min/max records per block from `XMBUF_BLOCKSIZE`.
- Allocate monotonically increasing fake block numbers.
- Free only the most recently allocated fake block by reducing `highest_bno`.
- Detach in-memory btree buffers from transactions during commit/cancel.
- Finalize dirty in-memory buffers directly to the backing xfile on commit.

## Root and Cursor Handling

`xfbtree_set_root` copies the new root pointer into `xfbt->root` and adjusts `xfbt->nlevels`.

`xfbtree_init_ptr_from_cur` initializes traversal from `xfbt->root`.

`xfbtree_dup_cursor` allocates a new generic btree cursor, copies flags, height, and `xfbtree` pointer, and holds the cursor group if present. It does not duplicate persistent root state because the root lives in the shared `struct xfbtree`.

## Initialization

`xfbtree_init` requires:

- The mount must support CRC metadata.
- The concrete btree must use long pointers.
- The caller must have set `xfbt->owner`.
- The caller supplies an `xfs_buftarg` backed by in-memory xfile storage.

It clears the `xfbtree`, records the target, computes leaf and node fanout from block size minus long CRC btree header length, sets `nlevels` to one, and creates an empty leaf block as the root.

`xfbtree_init_leaf_block` obtains an in-memory buffer for block zero, initializes it as a btree leaf with zero records, releases it, and stores the root pointer.

## Block Allocation and Freeing

`xfbtree_alloc_block` assigns the next `highest_bno`, verifies that the `xmbuf` target can represent the block address, stores it as a big-endian long pointer, and reports success through `stat`.

`xfbtree_free_block` only decrements `highest_bno` if the freed block is the most recently allocated block. It does not perform general free-space management, so allocation is append-like.

## Record Geometry

`xfbtree_get_minrecs` and `xfbtree_get_maxrecs` return precomputed leaf or node fanout from `xfbt->minrecs[level != 0]` and `xfbt->maxrecs[level != 0]`.

This makes in-memory btrees compatible with generic balancing and bulk-loading code.

## Transaction Commit and Cancel

In-memory btree buffers cannot be committed through the normal filesystem log because they are ephemeral repair data. The file therefore scans transaction log items for buffer items whose target matches `xfbt->target`.

`xfbtree_trans_commit`:

- Finds matching buffer log items.
- Detaches them from the transaction with `xmbuf_trans_bdetach`.
- Finalizes each buffer to the xfile with `xmbuf_finalize`.
- Releases each buffer.
- Preserves the transaction dirty flag only if non-xfbtree items remain dirty.
- Continues detaching all xfbtree buffers even if one finalize fails.

`xfbtree_trans_cancel`:

- Detaches and releases xfbtree buffers without undoing changes.
- Recomputes the transaction dirty flag from remaining non-xfbtree items.
- Documents that callers must not access the btree after cancel because changes are not rolled back.

## Integration Points

This file plugs into `xfs_btree_ops` callbacks for memory btrees:

- `set_root`
- `init_ptr_from_cur`
- `dup_cursor`
- `alloc_block`
- `free_block`
- `get_minrecs`
- `get_maxrecs`

It also depends on `xfs_buf_mem`/`xmbuf` APIs, transaction item lists, buffer log items, tracing, and generic btree block initialization.

## Important Invariants

- In-memory btrees use long-format CRC btree blocks only.
- Fake block numbers convert to disk addresses through `xfbno_to_daddr`.
- `xfbt->target` must be an in-memory buffer target.
- Commit/cancel must remove all xfbtree buffers from a transaction before normal transaction processing continues.
- Cancel does not restore prior btree state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.h

## Purpose

`xfs_btree_mem.h` declares the in-memory XFS btree wrapper type and callback helpers used to adapt generic btree operations to `xmbuf`-backed ephemeral btrees.

## Key Definitions

`xfbno_t` is the fake block-number type for memory btrees.

The header defines conversions between fake btree block numbers and disk-address units:

- `xfbno_to_daddr`
- `xfs_daddr_to_xfbno`

The fake block size is tied to `XMBUF_BLOCKSIZE`, with sector-size conversion constants.

## `struct xfbtree`

`struct xfbtree` stores:

- The in-memory buffer target.
- The highest fake block number written.
- The owner value stored in btree block headers.
- The root btree pointer.
- The current tree height.
- Precomputed max/min records for leaf and node blocks.

This structure is the persistent state shared by cursors over an in-memory btree.

## Exported Interface

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, the header declares:

- Block validation: `xfbtree_verify_bno`.
- Root callbacks: `xfbtree_set_root`, `xfbtree_init_ptr_from_cur`.
- Cursor callback: `xfbtree_dup_cursor`.
- Geometry callbacks: `xfbtree_get_minrecs`, `xfbtree_get_maxrecs`.
- Allocation callbacks: `xfbtree_alloc_block`, `xfbtree_free_block`.
- Lifecycle: `xfbtree_init`, `xfbtree_destroy`.
- Transaction integration: `xfbtree_trans_commit`, `xfbtree_trans_cancel`.

When the option is disabled, `xfbtree_verify_bno` is stubbed to false.

## Integration Points

Concrete memory-backed btree operation tables use these functions as their generic `xfs_btree_ops` callbacks. Online repair code owns the `struct xfbtree`, supplies an `xfs_buftarg`, and uses the transaction helpers to keep ephemeral btree buffers out of normal log commit paths.

## Important Invariants

- Callers must set owner/target context before initialization as documented.
- The btree uses `xmbuf` block sizing.
- Memory btree blocks are addressed as long btree pointers.
- The disabled-config stub intentionally prevents accidental validation success.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.c

## Purpose

`xfs_btree_staging.c` implements staged btree rebuild support and the generic bulk loader for newly built btrees. It lets online repair and rebuild code construct a replacement btree behind a fake root, fill it from sorted records, and later atomically commit the new root into AG or inode metadata.

Staging cursors are intentionally restricted: regular btree modification operations are not supported. The bulk loader is the intended construction path.

## Fake Root Model

The file supports two fake root types:

- AG-rooted fake roots through `struct xbtree_afakeroot`.
- Inode-rooted fake roots through `struct xbtree_ifakeroot`.

A staging cursor points at these fake roots instead of live filesystem metadata. After bulk loading, the caller logs the real metadata root change and commits the fake root back into a normal cursor.

## AG-Rooted Staging

`xfs_btree_stage_afakeroot`:

- Requires a non-staging, non-inode, transactionless cursor.
- Stores `afake` in the cursor.
- Sets cursor height from `afake->af_levels`.
- Marks the cursor with `XFS_BTREE_STAGING`.

`xfs_btree_commit_afakeroot`:

- Requires a staging, transactionless cursor.
- Clears the fake root pointer.
- Restores the real AG buffer.
- Clears the staging flag.
- Attaches the transaction.

The caller must log the concrete AG root field before committing the staged cursor.

## Inode-Rooted Staging

`xfs_btree_stage_ifakeroot`:

- Requires an inode-rooted, non-staging, transactionless cursor.
- Stores the fake root.
- Sets cursor height from `ifake->if_levels`.
- Sets the cursor fork size and `XFS_STAGING_FORK`.
- Marks the cursor as staging.

`xfs_btree_commit_ifakeroot` clears fake-root state, restores the real fork selector, clears staging, and attaches the transaction.

The fake inode root owns a temporary `struct xfs_ifork`, block count, height, and available fork size.

## Bulk Load Workflow

The staged bulk-load sequence is:

1. Caller initializes a fake root and staging cursor.
2. Caller fills `struct xfs_btree_bload`.
3. Caller invokes `xfs_btree_bload_compute_geometry`.
4. Caller preallocates all blocks required by `bbl->nr_blocks`.
5. `xfs_btree_bload` formats blocks and loads sorted records.
6. Caller commits the staged root and later cleans up old btree blocks.

Preallocating all blocks avoids ENOSPC halfway through a rebuild and allows block placement policy to remain outside the loader.

## Buffer Handling

`xfs_btree_bload_drop_buf` marks a formatted buffer uptodate, queues it on an ordered delayed-write list, releases it, increments the dirty count, and submits the list when `max_dirty` is reached. The final loader submits all remaining buffers and cancels any list on error.

This bounds dirty buffer accumulation during large rebuilds.

## Block Preparation

`xfs_btree_bload_prep_block` creates one block at a given level:

- If the level is an inode root, it allocates `if_broot` memory through the caller’s `iroot_size` callback and initializes an inline root block.
- Otherwise it claims a preallocated block via `bbl->claim_block`.
- It gets the buffer for that block.
- It connects the previous block’s right sibling to the new block.
- It drops the previous buffer if needed.
- It initializes the new block header and left sibling.
- It returns the new pointer, buffer, and block.

This function is responsible for sibling linkage during level construction.

## Leaf Loading

`xfs_btree_bload_leaf` repeatedly calls `bbl->get_records` until the requested number of records has been written into the leaf block. The callback must return records in sorted order by setting cursor state and using concrete btree record initialization behavior.

A negative callback result aborts the load.

## Node Loading

`xfs_btree_bload_node` fills an internal block from lower-level child blocks:

- It reads the child block named by `child_ptr`.
- It copies `child_ptr` into the parent pointer slot.
- It derives the child low/high key summary through `xfs_btree_get_keys`.
- It copies the key into the parent.
- It advances `child_ptr` to the child’s right sibling.

This builds parent levels left-to-right from already formatted child levels.

## Geometry Calculation

`xfs_btree_bload_compute_geometry` determines final height and block count. It first normalizes slack:

- Negative slack means fill roughly halfway between min and max occupancy, generally about 75 percent full.
- Slack is capped so records per block never drops below minrecs for normal blocks.

For each level, `xfs_btree_bload_level_geometry` computes:

- Desired records/keyptrs per block.
- Number of blocks at this level.
- Average records per block.
- Count of leftmost blocks that receive one extra item.

Inode-rooted btrees are special because root geometry differs from regular blocks. The function recalculates level geometry when deciding whether contents fit in the inode root.

The final output fields are `bbl->nr_records`, `bbl->nr_blocks`, and `bbl->btree_height`. For inode-rooted btrees, the inline root is not counted in `nr_blocks`.

## Bulk Load Execution

`xfs_btree_bload`:

- Sets cursor height to the computed btree height.
- Loads leaf blocks first, distributing records evenly and remembering the leftmost leaf pointer.
- Drops/submits dirty buffers as configured.
- Builds each internal level from the child level’s sibling chain.
- Updates the fake root with root pointer, height, and block count.
- Submits all formatted buffers.
- Cancels outstanding delayed-write buffers and releases the current buffer on error.

For inode-rooted btrees, the top level can be an inline root and the fake root records `if_levels` and `if_blocks`. For AG-rooted btrees, the fake root records `af_root`, `af_levels`, and `af_blocks`.

## Integration Points

This file depends on generic btree layout/access helpers from `xfs_btree.c`, concrete btree callbacks supplied in `xfs_btree_ops`, caller-provided reservation/record callbacks from `xfs_btree_bload`, transactionless staging cursors, and delayed-write buffer submission.

It is primarily used by online repair and rebuild paths that need to construct replacement metadata off to the side.

## Important Invariants

- Staging cursors must be transactionless until committed.
- Bulk records must be supplied in sort order.
- All disk blocks must be preallocated and claimed through the loader callback.
- Regular btree modification paths must not be used on staging cursors.
- Inode-root bulk loading requires an `iroot_size` callback.
- The fake root is the only root visible until the caller commits it.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.h

## Purpose

`xfs_btree_staging.h` declares fake-root state and bulk-loading interfaces for staged XFS btree construction.

## Fake Root Types

`struct xbtree_afakeroot` tracks a staged AG-rooted btree:

- New root AG block.
- New height.
- Number of blocks used.

`struct xbtree_ifakeroot` tracks a staged inode-rooted btree:

- Temporary inode fork.
- Block count.
- Height.
- Available fork size.

These are stored in staging cursors while a replacement btree is being built.

## Stage and Commit APIs

The header declares:

- `xfs_btree_stage_afakeroot`
- `xfs_btree_commit_afakeroot`
- `xfs_btree_stage_ifakeroot`
- `xfs_btree_commit_ifakeroot`

Stage functions redirect a cursor to fake root state. Commit functions transform the cursor back to normal metadata-rooted operation after the caller logs the real root update.

## Bulk-Load Callbacks

The bulk loader is parameterized by:

- `xfs_btree_bload_get_records_fn`: supplies sorted records for leaf blocks.
- `xfs_btree_bload_claim_block_fn`: claims one preallocated block for formatting.
- `xfs_btree_bload_iroot_size_fn`: computes inline inode-root buffer size.

The loader does not allocate arbitrary filesystem space itself; callers must reserve and claim blocks.

## `struct xfs_btree_bload`

This structure contains loader callbacks, input record count, slack targets, computed block count and height, dirty-buffer flush thresholds, and dirty-buffer accounting.

Important fields:

- `nr_records`: caller input and geometry basis.
- `leaf_slack` / `node_slack`: free slots to leave in blocks, or negative for default 75 percent style loading.
- `nr_blocks`: computed number of external btree blocks.
- `btree_height`: computed tree height.
- `max_dirty`: delayed-write flush threshold.
- `nr_dirty`: runtime dirty buffer count.

## Exported Functions

- `xfs_btree_bload_compute_geometry`: prepares block count and height before allocation.
- `xfs_btree_bload`: formats and fills the staged btree.

## Integration Points

Concrete rebuild code includes this header to stage cursors and bulk-load replacement btrees. It must supply record iteration, block reservation/claiming, and inline-root sizing behavior suitable for the concrete btree type.

## Important Invariants

- Callers must compute geometry before loading.
- Callers must allocate all required blocks before `xfs_btree_bload`.
- Record callbacks must return records in sorted order.
- Slack values are advisory but bounded by btree min/max occupancy rules.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_cksum.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_cksum.h

## Purpose

`xfs_cksum.h` provides small inline CRC32c helper routines for XFS metadata buffers whose checksum field lives inside the buffer being checksummed.

## Main Helpers

`xfs_start_cksum_safe` computes an intermediate checksum without modifying the buffer. It calculates CRC32c over the bytes before the checksum field, feeds four zero bytes for the checksum field, and then continues over the rest of the buffer.

`xfs_start_cksum_update` is the faster mutable path. It zeroes the checksum field in place and computes CRC32c over the whole buffer. Callers must have exclusive access.

`xfs_end_cksum` converts the intermediate CRC to on-disk little-endian inverted format.

`xfs_update_cksum` zeroes the field, computes the checksum, finalizes it, and writes it back to the buffer.

`xfs_verify_cksum` computes the safe checksum and compares it with the stored finalized value.

## Constants

`XFS_CRC_SEED` is the CRC32c seed value, defined as all bits set.

## Integration Points

These helpers are used by XFS metadata buffer checksum wrappers such as btree block CRC calculation and verification. They rely on the kernel `crc32c` implementation and endian conversion helpers.

## Important Invariants

- Safe verification must not mutate the buffer.
- Update mode temporarily mutates the checksum field and therefore requires exclusive access.
- XFS stores CRC32c results in little-endian inverted form for consistent on-disk representation.
- The checksum offset must identify a 32-bit checksum field fully contained in the buffer.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_cksum.h -->