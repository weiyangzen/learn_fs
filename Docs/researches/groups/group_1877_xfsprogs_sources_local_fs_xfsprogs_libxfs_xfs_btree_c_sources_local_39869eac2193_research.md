# Group Research: group_1877_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_btree_c_sources_local_39869eac2193

Scope: `Docs/research_subset_a.md`

Files researched:

- `sources/local-fs/xfsprogs/libxfs/xfs_btree.c`
- `sources/local-fs/xfsprogs/libxfs/xfs_btree.h`
- `sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.c`
- `sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.h`
- `sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.c`
- `sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.h`
- `sources/local-fs/xfsprogs/libxfs/xfs_cksum.h`

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree.c

## Purpose

`xfs_btree.c` is the generic XFS btree engine used by xfsprogs libxfs. It implements shared block verification, cursor movement, lookup, insert, update, delete, balancing, split/join, block traversal, range query, owner rewrite, geometry calculation, cursor-cache setup, and inode-rooted metadata btree block allocation helpers.

Concrete XFS btrees such as allocation, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount plug into this engine through `struct xfs_btree_ops`.

This xfsprogs copy is the userspace libxfs version. Compared with the Linux kernel copy in this repository, the meaningful local difference in this file is the include environment: xfsprogs uses `xfs_platform.h`, `xfile.h`, and `buf_mem.h`, and omits kernel-only include dependencies such as log and quota internals. Kernel-only split worker code remains guarded by `#ifdef __KERNEL__`, so xfsprogs uses the direct split path.

## Block Model

The file treats all btree blocks as `struct xfs_btree_block` headers followed by either:

- leaf records, addressed by `xfs_btree_rec_addr`;
- internal low keys, optional high keys, and child pointers, addressed by `xfs_btree_key_addr`, `xfs_btree_high_key_addr`, and `xfs_btree_ptr_addr`.

All in-block record/key/pointer indexes are one-based.

The block header length depends on pointer format and CRC format:

- long pointer btrees use long-format headers for filesystem block or xfile block pointers;
- short pointer btrees use allocation-group block pointers;
- CRC-enabled filesystems use extended v5 headers with UUID, block number, owner, LSN, and CRC fields.

`xfs_btree_block_len`, `xfs_btree_rec_offset`, `xfs_btree_key_offset`, `xfs_btree_high_key_offset`, and `xfs_btree_ptr_offset` centralize this layout math.

## Btree Types

The generic code dispatches on `cur->bc_ops->type`:

- `XFS_BTREE_TYPE_AG`: short-pointer AG-rooted btrees.
- `XFS_BTREE_TYPE_INODE`: long-pointer inode-rooted btrees with roots stored in inode forks.
- `XFS_BTREE_TYPE_MEM`: long-pointer in-memory xfile-backed btrees used by repair/staging workflows.

Helpers such as `xfs_btree_buftarg`, `xfs_btree_bbsize`, `xfs_btree_ptr_to_daddr`, `xfs_btree_buf_to_ptr`, and pointer verification routines abstract these address spaces.

## Verification and Corruption Handling

The top of the file implements btree block and pointer verification.

Header checks include:

- magic number via `xfs_btree_magic`;
- expected level;
- maximum record count for the level;
- CRC-format metadata UUID;
- buffer disk address;
- owner fields when enough cursor context exists;
- long-format padding;
- sibling pointers.

Sibling pointer checks reject self-references and out-of-range addresses. Separate helpers cover filesystem block siblings, memory-backed xfile siblings, and AG block siblings.

Main verification entry points:

- `__xfs_btree_check_block`
- `xfs_btree_check_block`
- `__xfs_btree_check_ptr`
- `xfs_btree_check_ptr`
- `xfs_btree_check_block_owner`
- `xfs_btree_fsblock_v5hdr_verify`
- `xfs_btree_fsblock_verify`
- `xfs_btree_memblock_verify`
- `xfs_btree_agblock_v5hdr_verify`
- `xfs_btree_agblock_verify`

On verifier failure, the code marks the btree sick through health reporting, marks corrupt buffers where applicable, traces corruption, and returns `-EFSCORRUPTED`.

## CRC Helpers

The file provides btree-specific wrappers around buffer checksum logic:

- `xfs_btree_fsblock_calc_crc`
- `xfs_btree_fsblock_verify_crc`
- `xfs_btree_agblock_calc_crc`
- `xfs_btree_agblock_verify_crc`

For CRC filesystems, these helpers validate log sequence numbers and update/verify CRC fields at the correct long- or short-header offsets. When calculating CRCs, the LSN is copied from the buffer log item if available.

## Cursor Lifecycle

`xfs_btree_del_cursor` releases cursor buffers, drops held group references, checks bmap allocation accounting, and frees the cursor from its cache.

`xfs_btree_dup_cursor` duplicates a cursor by calling the concrete btree `dup_cursor` operation, copying cursor record and level state, and re-reading each attached buffer. Staging cursors cannot be duplicated because staged rebuild cursors are intended to be private.

`xfs_btree_setbuf` swaps a cursor-level buffer, releases any old buffer, clears readahead state, and records when left or right sibling readahead is unnecessary because the sibling pointer is null.

## Buffer and Block Initialization

The file initializes headers through:

- `__xfs_btree_init_block`
- `xfs_btree_init_block`
- `xfs_btree_init_buf`
- `xfs_btree_init_block_cur`

These functions set magic, level, record count, null siblings, block number, owner, UUID, LSN, and buffer ops.

`xfs_btree_owner` computes the expected owner from the btree type:

- memory btrees use `xfbtree->owner`;
- inode btrees use the inode number;
- AG btrees use the group number.

## Logging Helpers

Changes are logged by field and region:

- `xfs_btree_log_keys`
- `xfs_btree_log_recs`
- `xfs_btree_log_ptrs`
- `xfs_btree_log_block`

For inode-rooted in-fork roots, logging maps to inode fork-root log flags. For buffer-backed blocks, logging marks buffers as btree buffers and logs byte ranges. CRC fields are intentionally not logged directly because recovery regenerates checksums.

## Lookup and Cursor Movement

`xfs_btree_lookup` performs root-to-leaf binary search using btree-specific `cmp_key_with_cur`. It supports exact, less-or-equal, and greater-or-equal searches, handles empty single-leaf trees, and fixes cursor positioning when a GE lookup lands beyond the current block but a right sibling exists.

`xfs_btree_lookup_get_block` reads or reuses the block for a level, validates owner and level, rejects empty internal nodes, and attaches the buffer to the cursor.

`xfs_btree_increment` and `xfs_btree_decrement` move a cursor forward or backward at any level. They handle in-block movement, sibling crossing, upward parent-pointer adjustment, downward buffer reloads, and directional sibling readahead.

`xfs_btree_goto_left_edge` positions a cursor before the first record by looking up the zero key and decrementing.

`xfs_btree_has_more_records` reports whether the current leaf has further records or a right sibling.

## Key Propagation

For regular btrees, parent keys need updates mainly when the first record/key in a child changes.

For overlapping interval btrees, internal nodes carry both low and high key summaries. The high key can come from any child record, so the core must recompute and propagate high-key summaries more aggressively.

Important helpers:

- `xfs_btree_high_key_from_key`
- `xfs_btree_get_leaf_keys`
- `xfs_btree_get_node_keys`
- `xfs_btree_get_keys`
- `xfs_btree_needs_key_update`
- `__xfs_btree_updkeys`
- `xfs_btree_updkeys_force`
- `xfs_btree_update_keys`

## Insert Path

`xfs_btree_insert` builds a record and key from the cursor, then repeatedly calls `xfs_btree_insrec` from leaf toward root until no split pointer remains.

`xfs_btree_insrec`:

- validates cursor location;
- makes full blocks non-full;
- shifts keys/pointers or records to open an insertion slot;
- copies the new entry;
- logs changed ranges and record counts;
- propagates key changes;
- returns split information to the next level.

`xfs_btree_make_block_unfull` tries, in order:

1. expand or promote an inode-rooted in-fork root;
2. shift one entry to the right sibling;
3. shift one entry to the left sibling;
4. split the block.

`__xfs_btree_split` allocates a right sibling, divides records/keyptrs between left and right blocks, fixes sibling links, updates neighboring sibling backpointers, computes the new block key, and may create a duplicate cursor for parent insertion.

In xfsprogs builds, `xfs_btree_split` is a direct alias for `__xfs_btree_split`; the kernel-only worker-thread split path is excluded.

## Root Promotion

Inode-rooted btrees can start with a root stored directly in the inode fork. When that root cannot grow further:

- `xfs_btree_new_iroot` allocates a real btree block and copies root contents into it.
- `xfs_btree_promote_leaf_iroot` promotes a leaf root into a node root pointing at a new child block.
- `xfs_btree_promote_node_iroot` promotes a node root by copying key/pointer entries into a child and increasing tree height.

External-root btrees use `xfs_btree_new_root` after a root split. Staging cursors update fake roots through `xfs_btree_set_root`.

## Update Path

`xfs_btree_update` overwrites the current leaf record, logs the record range, and updates parent keys if the modified position can affect low/high key summaries.

This gives regular and overlapping btrees a shared update path while preserving interval-tree high-key correctness.

## Delete and Rebalance Path

`xfs_btree_delete` repeatedly calls `xfs_btree_delrec` from leaf upward while joins require removal of parent key/pointer entries.

`xfs_btree_delrec`:

- removes the selected record or key/pointer;
- shifts remaining entries left;
- decrements and logs record count;
- shrinks inode-rooted roots where possible;
- collapses external roots with one child;
- updates parent keys when needed;
- returns early if the block remains above minimum occupancy;
- attempts single-record rebalancing from right or left siblings;
- joins with a sibling when rebalancing is insufficient;
- frees the removed block.

For overlapping btrees, if block joins occurred, `xfs_btree_delete` force-updates high keys after the upward deletion sequence.

Root collapse helpers:

- `xfs_btree_demote_leaf_child`
- `xfs_btree_demote_node_child`
- `xfs_btree_kill_iroot`
- `xfs_btree_kill_root`

## Traversal and Owner Rewrite

`xfs_btree_visit_blocks` walks every btree level left-to-right using sibling pointers. It supports visiting internal levels, leaf levels, or both. `xfs_btree_visit_block` detects self-referential right siblings to avoid cyclic traversal.

`xfs_btree_change_owner` uses the visitor to rewrite owner fields throughout CRC-format btrees. With a transaction, it uses ordered buffer logging where possible and can return `-EAGAIN` when a normal log is needed. Without a transaction, it queues buffers for delayed write.

## Range Queries

The file supports both ordinary sorted btrees and overlapping interval btrees.

`xfs_btree_query_range` converts incore low/high records to keys, validates ordering, and dispatches to:

- `xfs_btree_simple_query_range` for non-overlapping btrees;
- `xfs_btree_overlapped_query_range` for interval btrees.

The simple query uses LE lookup and forward iteration. The overlapped query performs depth-first traversal using internal low/high key summaries to prune subtrees.

`xfs_btree_query_all` scans all records using all-zero and all-ones key bounds.

`xfs_btree_has_records` classifies a key range as empty, sparse, or full by querying matching records and testing key contiguity through the concrete btree callback. It supports masked key comparisons for callers that intentionally ignore parts of the key.

## Geometry and Sizing

The file provides common sizing helpers:

- `xfs_btree_compute_maxlevels`
- `xfs_btree_calc_size`
- `xfs_btree_space_to_height`

These calculate tree height and block consumption from per-level fanout limits.

## Cursor Cache Initialization

`xfs_btree_init_cur_caches` initializes cursor caches for allocation, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount btrees. On failure it unwinds through `xfs_btree_destroy_cur_caches`.

`xfs_btree_destroy_cur_caches` destroys all these caches.

## Metadata-File Block Helpers

`xfs_btree_alloc_metafile_block` and `xfs_btree_free_metafile_block` allocate and free one block for inode-rooted metadata btrees. They require a metadata directory inode, use metadata-file AG reservation accounting, set rmap owner information for the inode/fork, and update metadata-file reserved space counters.

## Dependencies

This file depends heavily on:

- `xfs_btree.h` for cursor, ops, keys, records, and exported APIs;
- concrete btree modules for ops and cursor caches;
- transaction and buffer APIs;
- xfsprogs xfile/memory-buffer support for in-memory btrees;
- health reporting for sick metadata;
- staging fake-root APIs from `xfs_btree_staging.h`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree.h

## Purpose

`xfs_btree.h` is the public generic btree interface for libxfs. It defines the generic pointer, key, record, incore-record, cursor, operation-vector, traversal, query, verification, and helper APIs used by all XFS btree implementations.

The header is byte-identical to the Linux-stable copy in this repository.

## Generic Disk Wrappers

The file defines generic disk-format unions:

- `union xfs_btree_ptr`: short 32-bit AG block pointers or long 64-bit pointers.
- `union xfs_btree_key`: allocation, inode allocation, bmap, rmap, and refcount key storage.
- `union xfs_btree_rec`: allocation, inode allocation, bmap, rmap, and refcount record storage.

Overlapping btrees reserve enough key space for low/high key pairs.

`union xfs_btree_irec` defines incore records used by callers before concrete btree ops convert them to disk-format records and keys.

## Operation Vector

`struct xfs_btree_ops` is the core plug-in contract for concrete btrees. It supplies:

- btree name and type;
- geometry flags;
- key, pointer, and record sizes;
- buffer ops;
- stats and health metadata;
- cursor duplication/update callbacks;
- root pointer update callback;
- block allocation/free callbacks;
- min/max/disk-max record calculations;
- record/key initialization callbacks;
- key comparison callbacks;
- order checks for debug validation;
- key contiguity callback for sparse/full range classification;
- inode fork-root reallocation callback.

Geometry flags include:

- `XFS_BTGEO_OVERLAPPING`: internal nodes store interval summaries.
- `XFS_BTGEO_IROOT_RECORDS`: inode fork roots can store records directly.

## Cursor Structure

`struct xfs_btree_cur` carries transaction, mount, ops, cache, flags, current incore record, current height, max height, group reference, type-specific root context, per-format private counters, and a flexible array of `struct xfs_btree_level`.

Per-type cursor context includes:

- inode-rooted cursor state: inode, fork size, fork selector, staging fake root;
- AG-rooted cursor state: AG buffer and AG fake root;
- memory-backed cursor state: `struct xfbtree`.

Per-level state includes:

- current buffer;
- one-based current key/record pointer;
- left/right sibling readahead flags.

`xfs_btree_cur_sizeof` computes the allocation size for a cursor with a given height.

## Cursor Flags

Defined cursor flags include:

- `XFS_BTREE_STAGING`: cursor root is a fake staging root.
- `XFS_BTREE_BMBT_WASDEL`: bmap conversion from delayed allocation.
- `XFS_BTREE_BMBT_INVALID_OWNER`: skip owner check for extent swap.
- `XFS_BTREE_ALLOCBT_ACTIVE`: active allocation btree cursor.

## Exported Core APIs

The header declares generic operations implemented in `xfs_btree.c`:

- cursor lifecycle: `xfs_btree_del_cursor`, `xfs_btree_dup_cursor`;
- block verification: `xfs_btree_check_block`, `__xfs_btree_check_block`, `__xfs_btree_check_ptr`;
- block initialization: `xfs_btree_init_buf`, `xfs_btree_init_block`, `xfs_btree_init_block_cur`;
- lookup and movement: `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`;
- mutation: `xfs_btree_update`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_new_iroot`;
- traversal and query: `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_visit_blocks`;
- block counting and owner rewrite;
- CRC helpers;
- geometry helpers;
- cursor cache initialization/destruction;
- metadata-file block allocation/free helpers.

## Inline Helpers

The header provides inline helpers for:

- getting and setting `bb_numrecs`;
- reading block level;
- min/max macros for XFS numeric types;
- key comparisons with and without masks;
- determining whether a cursor is at an inode-rooted fork root;
- testing whether a cursor points to the last block at a level;
- allocating cursors from concrete cursor caches.

`xbtree_key_contig` classifies adjacent numeric key fields as gap, contiguous, or overlap and underpins `xfs_btree_has_records`.

## Traversal and Query Contracts

`xfs_btree_query_range_fn` callbacks receive each matching record and return zero to continue or nonzero to stop. `-ECANCELED` is reserved as an intentional stop code because query code does not generate it internally.

`xfs_btree_visit_blocks_fn` callbacks receive each visited block and its level. Flags select record blocks, leaf/internal blocks, or all blocks.

## Dependencies

This header is the central API shared by all concrete XFS btree implementations, in-memory btree support, and staging/bulk-load code.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.c

## Purpose

`xfs_btree_mem.c` implements xfile-backed in-memory btree support. These btrees use the generic btree engine with `XFS_BTREE_TYPE_MEM`, storing blocks in an in-memory buffer target rather than filesystem metadata blocks.

This support is used by repair and staging workflows that need temporary btree indexes whose contents can be discarded after the operation.

The file is byte-identical to the Linux-stable copy in this repository.

## Root and Cursor Operations

The file provides generic ops suitable for concrete memory-backed btrees:

- `xfbtree_set_root`: updates the in-memory root pointer and height.
- `xfbtree_init_ptr_from_cur`: initializes traversal from `xfbtree->root`.
- `xfbtree_dup_cursor`: allocates a duplicate cursor, copies flags and height, shares the `xfbtree`, and holds the group reference if present.

These functions assert that the cursor type is `XFS_BTREE_TYPE_MEM`.

## Lifecycle

`xfbtree_init` prepares an empty in-memory btree:

- requires a CRC-enabled filesystem;
- requires long btree pointers;
- clears the `struct xfbtree`;
- attaches the caller-provided memory buffer target;
- computes min/max records for leaf and node blocks from `XMBUF_BLOCKSIZE`;
- starts at height 1;
- initializes an empty leaf block as the root.

Callers must set `xfbt->owner` before initialization.

`xfbtree_destroy` drains the memory buffer target.

## Block Allocation

`xfbtree_alloc_block` allocates monotonically increasing xfile block numbers using `highest_bno`. It verifies the resulting address against the memory buffer target before returning it as a long btree pointer.

`xfbtree_free_block` observes freed block numbers and decrements `highest_bno` only when the highest-numbered block is freed. It does not maintain a general free list.

This allocation model is simple and sufficient for temporary btrees.

## Geometry

`xfbtree_get_minrecs` and `xfbtree_get_maxrecs` return leaf or node geometry from `xfbtree->minrecs` and `xfbtree->maxrecs`.

`xfbtree_rec_bytes` computes usable record space by subtracting the long-format CRC btree header from the memory buffer block size.

## Transaction Commit and Cancel

Temporary memory btrees still attach buffers to xfs transactions to coordinate locking and updates. They cannot rely on normal transaction commit persistence because the backing xfile is ephemeral.

`xfbtree_trans_commit`:

- scans transaction log items;
- finds buffer log items belonging to the `xfbtree` target;
- detaches those buffers from the transaction;
- finalizes them to the xfile with `xmbuf_finalize`;
- releases all matching buffers even if one finalize fails;
- recalculates the transaction dirty flag for remaining non-xfbtree items.

`xfbtree_trans_cancel` similarly detaches and releases all xfbtree buffers but does not undo changes. Callers must not access the btree after cancellation.

## Dependencies

The implementation depends on:

- `xfs_btree.c` for generic btree operation;
- `xfs_btree_mem.h` for `struct xfbtree` and address conversion;
- xfsprogs `xfile` and `buf_mem` support;
- transaction item lists and buffer log item plumbing;
- tracepoints for create, init, alloc/free, commit, and cancel events.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.h

## Purpose

`xfs_btree_mem.h` declares the in-memory xfile-backed btree interface. It defines xfile btree block numbers, address conversion helpers, the `struct xfbtree` header, and function declarations for memory-backed btree operations.

The file is byte-identical to the Linux-stable copy in this repository.

## Address Model

`xfbno_t` is a 64-bit xfile btree block number.

Constants derive xfile btree block sizing from xmbuf block sizing:

- `XFBNO_BLOCKSIZE`
- `XFBNO_BBSHIFT`
- `XFBNO_BBSIZE`

Conversion helpers:

- `xfbno_to_daddr`
- `xfs_daddr_to_xfbno`

These convert between xfile btree block numbers and XFS disk-address units so the generic buffer/btree code can address memory-backed blocks through normal buffer interfaces.

## `struct xfbtree`

`struct xfbtree` stores:

- memory buffer target;
- highest block number written;
- owner value;
- generic root pointer;
- tree height;
- max records for leaf/node blocks;
- min records for leaf/node blocks.

This structure is the root context stored in `cur->bc_mem.xfbtree`.

## Conditional API

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, the header exposes:

- block verification: `xfbtree_verify_bno`;
- root operations: `xfbtree_set_root`, `xfbtree_init_ptr_from_cur`;
- cursor duplication;
- min/max record callbacks;
- block allocation/free callbacks;
- initialization/destruction;
- transaction commit/cancel helpers.

When the config is disabled, `xfbtree_verify_bno` is defined as always false, preventing accidental validation success without memory-btree support.

## Dependencies

The header depends on xmbuf constants and generic btree cursor/types. It is consumed by `xfs_btree.c`, `xfs_btree_mem.c`, and concrete in-memory btree users.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.c

## Purpose

`xfs_btree_staging.c` implements fake-root staging cursors and the generic btree bulk loader. It is used to construct replacement XFS btrees privately, then commit the new root atomically into live metadata.

The file is byte-identical to the Linux-stable copy in this repository.

## Staging Cursor Model

A staging cursor has `XFS_BTREE_STAGING` set and points to a fake root instead of live AG or inode metadata. Regular btree queries and mutations are not supported for staging cursors; they are intended for bulk loading only.

Two fake-root families are supported:

- AG-rooted fake roots via `struct xbtree_afakeroot`.
- Inode-rooted fake roots via `struct xbtree_ifakeroot`.

## AG-Rooted Fake Roots

`xfs_btree_stage_afakeroot`:

- requires a non-inode btree cursor;
- requires no transaction;
- installs the fake root;
- copies fake-root height to the cursor;
- sets staging mode.

`xfs_btree_commit_afakeroot`:

- requires staging mode and no current transaction;
- clears the fake root;
- restores the real AG buffer and transaction;
- clears staging mode.

The caller must log the root change before commit.

## Inode-Rooted Fake Roots

`xfs_btree_stage_ifakeroot`:

- requires an inode-rooted cursor;
- requires no transaction;
- installs the fake inode fork root;
- copies fake-root height and fork size to the cursor;
- switches cursor fork selection to `XFS_STAGING_FORK`;
- sets staging mode.

`xfs_btree_commit_ifakeroot`:

- clears the fake inode root;
- restores the real fork selector and transaction;
- clears staging mode.

The caller must log the root change before commit.

## Bulk Loading Workflow

The bulk-loader comments describe the intended sequence:

1. Initialize a fake root.
2. Create a staging cursor.
3. Fill an `xfs_btree_bload` descriptor.
4. Call `xfs_btree_bload_compute_geometry`.
5. Preallocate every block reported in `nr_blocks`.
6. Call `xfs_btree_bload`.
7. Commit the staged root.
8. Clean up old btree blocks outside this generic code.

Bulk loading requires preallocated blocks to avoid ENOSPC failures midway through a rebuild and to improve locality.

## Dirty Buffer Handling

`xfs_btree_bload_drop_buf` marks newly formatted buffers uptodate, queues them for delayed write, releases the caller’s reference, and optionally flushes the delayed-write list after `max_dirty` buffers.

This prevents very large rebuilds from accumulating unbounded dirty buffers.

## Block Preparation

`xfs_btree_bload_prep_block` prepares the next block at a level.

For inode-rooted root levels:

- it allocates an incore fork-root buffer using the caller’s `iroot_size` callback;
- initializes the root block;
- returns no buffer pointer because the root lives in the inode fork;
- sets the block pointer to null.

For normal buffer-backed blocks:

- it claims a preallocated block via `claim_block`;
- obtains a buffer through generic btree helpers;
- updates the previous block’s right sibling pointer;
- drops the previous buffer to the delayed-write list;
- initializes the new block;
- sets its left sibling pointer;
- updates output pointers to the new block.

## Leaf Loading

`xfs_btree_bload_leaf` repeatedly calls the caller’s `get_records` callback until the requested number of records has been loaded into a leaf block.

The callback is responsible for returning records in btree sort order and usually does so by setting `cur->bc_rec` and using the concrete btree’s record initializer.

## Node Loading

`xfs_btree_bload_node` fills an internal node with key/pointer pairs:

- reads each child block;
- copies the child pointer into the node;
- derives child low/high keys with `xfs_btree_get_keys`;
- stores those keys in the parent;
- advances to the child’s right sibling;
- releases the child buffer.

This preserves both regular and overlapping-btree key summaries.

## Geometry Calculation

The loader computes tree geometry from record count, min/max records, and slack settings.

`xfs_btree_bload_ensure_slack` normalizes slack:

- negative slack means approximately 75 percent full;
- slack is capped so non-root blocks cannot fall below minimum occupancy.

`xfs_btree_bload_max_npb` computes the maximum entries to install at a level, respecting inode-root capacity for roots and subtracting leaf/node slack for ordinary blocks.

`xfs_btree_bload_desired_npb` enforces minimum occupancy for non-root blocks and at least one entry for roots.

`xfs_btree_bload_level_geometry` computes, for a level:

- average entries per block;
- number of blocks;
- number of blocks receiving one extra entry due to uneven division.

It spreads records/keyptrs as evenly as possible while never exceeding max records.

`xfs_btree_bload_compute_geometry` computes final height and block count from leaves upward. Inode-rooted btrees require repeated recalculation because inode fork-root capacity differs from ordinary block capacity. For inode-rooted btrees, the incore inode root is excluded from `nr_blocks`.

## Bulk Load Execution

`xfs_btree_bload` builds the staged btree bottom-up:

- loads all leaf blocks first;
- records the leftmost pointer for the next level;
- drops dirty buffers as it progresses;
- iteratively loads internal levels;
- tracks total block count;
- records the final root into the fake root;
- submits all delayed-write buffers;
- cancels remaining delayed writes and releases the current buffer on error.

For AG-rooted btrees it records root AG block, height, and block count in `afake`. For inode-rooted btrees it records height and block count in `ifake`.

## Dependencies

This file depends on:

- generic btree helpers from `xfs_btree.c`;
- staging structures from `xfs_btree_staging.h`;
- buffer delayed-write APIs;
- concrete btree callbacks supplied through `xfs_btree_bload`;
- tracepoints for staging and block loading.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.h

## Purpose

`xfs_btree_staging.h` declares fake-root structures and the bulk-load API for constructing staged XFS btrees. It is the public interface implemented by `xfs_btree_staging.c`.

The file is byte-identical to the Linux-stable copy in this repository.

## AG Fake Root

`struct xbtree_afakeroot` stores:

- `af_root`: AG block number of the new btree root;
- `af_levels`: staged btree height;
- `af_blocks`: number of blocks used.

The header declares:

- `xfs_btree_stage_afakeroot`
- `xfs_btree_commit_afakeroot`

## Inode Fake Root

`struct xbtree_ifakeroot` stores:

- fake inode fork pointer;
- number of blocks used;
- staged btree height;
- bytes available in the inode fork.

The header declares:

- `xfs_btree_stage_ifakeroot`
- `xfs_btree_commit_ifakeroot`

## Bulk-Load Callback Types

The bulk loader is parameterized by three callbacks:

- `xfs_btree_bload_get_records_fn`: load sorted records into a leaf block.
- `xfs_btree_bload_claim_block_fn`: claim one preallocated block and return it as a generic btree pointer.
- `xfs_btree_bload_iroot_size_fn`: compute incore inode-root size for inode-rooted btrees.

## `struct xfs_btree_bload`

`struct xfs_btree_bload` carries both caller configuration and computed geometry:

- callbacks for records, block claiming, and inode-root sizing;
- planned record count;
- leaf and node slack;
- computed block count;
- computed btree height;
- dirty-buffer flush threshold;
- current dirty-buffer count.

Negative slack means the geometry code computes a default that leaves blocks roughly 75 percent full. Slack is not enforced on inode root blocks.

## Public API

The header declares:

- `xfs_btree_bload_compute_geometry`
- `xfs_btree_bload`

Callers must preallocate all blocks reported by geometry before invoking the actual bulk load.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_cksum.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_cksum.h

## Purpose

`xfs_cksum.h` provides small inline CRC32c helpers for XFS metadata buffers. It supports both checksum verification without modifying a buffer and checksum generation by temporarily zeroing the checksum field.

## CRC Seed

`XFS_CRC_SEED` is defined as the bitwise inverse of zero as a 32-bit value. All helper calculations start from this seed.

## Safe Verification Path

`xfs_start_cksum_safe` computes the intermediate checksum for a buffer without modifying the buffer. It:

1. computes CRC32c from the beginning of the buffer up to the checksum field;
2. feeds a zero 32-bit value for the checksum field;
3. computes CRC32c over the remainder of the buffer.

This is used when verifying metadata because verification should not alter the buffer contents.

`xfs_verify_cksum` compares the stored little-endian checksum field to `xfs_end_cksum` of the safe intermediate CRC.

## Update Path

`xfs_start_cksum_update` is the faster generation path for callers with exclusive buffer access. It zeroes the checksum field in the buffer and calculates CRC32c over the whole buffer in one pass.

`xfs_update_cksum` computes the checksum with that update path and writes the final checksum back into the buffer.

## Finalization

`xfs_end_cksum` converts the intermediate CRC to the final ondisk format by complementing the little-endian value. The comment notes that CRC32c returns host-endian results but XFS stores the checksum consistently in little-endian format.

## Dependencies

This header depends on `crc32c`, endian helpers, and XFS integer typedefs. Btree CRC helpers in `xfs_btree.c` ultimately rely on this style of checksum logic through buffer checksum wrappers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_cksum.h -->