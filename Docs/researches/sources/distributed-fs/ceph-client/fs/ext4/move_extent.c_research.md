# sources/distributed-fs/ceph-client/fs/ext4/move_extent.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/move_extent.c` implements ext4 online defragmentation through `ext4_move_extents()`. It swaps mapped extents between an original file and a donor file, optionally preserving original data by copying page-cache contents across the newly swapped mapping. The source was read as a complete 658-line file.

## Important APIs, Types, and Functions

The public entry point is `ext4_move_extents(struct file *o_filp, struct file *d_filp, __u64 orig_blk, __u64 donor_blk, __u64 len, __u64 *moved_len)`. Shared locking helpers `ext4_double_down_write_data_sem()` and `ext4_double_up_write_data_sem()` serialize extent-tree mutations across the two inodes by address order. `struct mext_data` carries the original inode, donor inode, current original mapping, and donor logical block.

Core helpers are `mext_check_validity()` for filesystem and inode constraints, `mext_check_adjust_range()` for block range alignment and EOF trimming, `mext_move_extent()` for one folio-bounded move, `mext_move_begin()` for double folio locking and mapping revalidation, `mext_folio_mkuptodate()` for reading source buffers into cache, and `mext_folio_mkwrite()` for rebuilding buffer mappings and committing dirty data after the swap.

## Control Flow

`ext4_move_extents()` locks both non-directory inodes against truncate, validates that files are regular, extent-based, same-filesystem, non-DAX, non-encrypted, non-journal-data, non-swap, non-quota, and non-empty, waits for direct I/O, adjusts the requested range, then loops over original mappings from `ext4_map_blocks()`. Holes and delayed allocations are skipped; mapped or unwritten ranges are handed to `mext_move_extent()`.

`mext_move_extent()` starts a move-extents journal transaction and marks fast commit ineligible. `mext_move_begin()` locks the relevant folios in stable inode order, waits for writeback, verifies that the original extent-status sequence still matches the mapping observed before folio locking, trims the move to folio and donor mapping boundaries, then classifies the work as skip, pure extent move, or data copy. For data-copy moves, the original folio range is made uptodate before buffer mappings are released. The code then write-locks both `i_data_sem` locks and calls `ext4_swap_extents()`. If original data must survive, it remaps the original folio buffers through `mext_folio_mkwrite()` and pins the written range to the transaction with `ext4_jbd2_inode_add_write()`.

Short progress is folded into the outer loop. `-ESTALE` retries after extent-status sequence changes, `-ENOSPC` uses `ext4_should_retry_alloc()`, and `-EBUSY` can force a nested journal commit before retrying. If data copy fails after a swap, the repair branch swaps the moved extent back; failure to repair is escalated with `ext4_error_inode_block()`.

## State and Persistence Behavior

Persistent changes are extent-tree swaps between the original and donor inode plus possible data writes to the original file after the swap. The operation dirties journal metadata and explicitly excludes fast commit because extent movement cannot be replayed by the fast-commit path. For data-copy cases, page-cache data is preserved by reading before the swap and committing writes after the mapping replacement. `*moved_len` accumulates successfully swapped blocks, and successful moves discard both inodes' preallocations to avoid stale allocation hints.

Transient state includes locked folios, buffer heads, current `ext4_map_blocks` records, journal credits sized from `ext4_chunk_trans_extent()`, and retry counters.

## Dependencies and Integration Points

This file depends on ext4 extents (`ext4_map_blocks()`, `ext4_swap_extents()`), the extent status sequence (`i_es_seq`), JBD2 transaction handling, folio and buffer-head cache operations, direct-I/O exclusion, quota-file detection, mount feature checks, and ext4 tracepoints `trace_ext4_move_extent_enter/exit`. It is called by the defragmentation ioctl path and coordinates with writeback, truncate, and allocation retry logic.

## Risks and Edge Cases

High-risk areas are stale mapping detection, folio order and inode lock ordering, data preservation after extent swap, and repair after partial failure. The range must share the same page offset in both files, so unaligned donor/original starts are rejected. Bigalloc, DAX, encrypted files, journaled-data mode, swap files, and quota files are rejected because the swap/copy semantics are unsafe or unsupported. If `filemap_release_folio()` fails, the move returns `-EBUSY`; this protects against buffers that cannot be invalidated before the extent tree is swapped.

## Test Signals

Useful tests include online defrag of mapped, unwritten, sparse, and mixed extents; donor holes; EOF-shortened ranges; concurrent writeback causing `-ESTALE`; direct-I/O wait coverage; `-ENOSPC` retry; `-EBUSY` retry after journal commit; and fault injection around `ext4_swap_extents()`, folio read, and post-swap write. Signals include `trace_ext4_move_extent_*`, changed `moved_len`, journal abort or ext4 error logs on failed repair, and verification that original file data remains intact.
