# sources/distributed-fs/ceph-client/fs/ntfs/bitmap.c

## Purpose

`bitmap.c` implements NTFS bitmap operations for cluster trimming and setting or clearing ranges of bits in bitmap attributes. It is used for volume free-space discard and metadata bitmap mutation.

## Important APIs, Types, And Functions

- `ntfs_trim_fs(struct ntfs_volume *vol, struct fstrim_range *range)` scans the volume cluster bitmap for zero bits, aligns free ranges to the block device discard granularity, issues discard requests, and returns the total trimmed byte count in `range->len`.
- `__ntfs_bitmap_set_bits_in_run(struct inode *vi, s64 start_bit, s64 count, u8 value, bool is_rollback)` sets or clears a bitmap bit range across one or more folios and rolls back already modified bits if a later folio cannot be mapped.

## Control Flow And Algorithms

Trim converts byte start/length into cluster bounds, allocates a file readahead state, reads cluster-bitmap folios, and interprets each page as an `unsigned long` bitset. It uses `find_next_zero_bit()` to locate free runs and `find_next_bit()` to find their end. Each run is converted back to bytes, aligned to discard granularity, checked against `range->minlen`, and discarded with `blkdev_issue_discard()`.

Bitmap mutation computes the first and last folio indices containing the range, maps the first folio, handles a partial first byte bit-by-bit, fills full bytes with `memset()`, advances through intermediate folios, and handles a partial final byte. Each folio is marked dirty and unlocked. If a subsequent folio read fails, the function recursively calls itself in rollback mode to invert the already modified prefix.

## State And Persistence Behavior

Bitmap changes are made in the target bitmap inode's page cache and marked dirty for writeback. When mutating the volume `$Bitmap` (`FILE_Bitmap`), it also calls `ntfs_set_lcn_empty_bits()` to update auxiliary free-space accounting for the affected bits. Trim does not change NTFS metadata; it informs the block device that free clusters can be discarded.

## Dependencies And Integration Points

The file depends on Linux bit operations, block discard APIs, folio mapping, and NTFS helpers such as `ntfs_bytes_to_cluster()`, `ntfs_cluster_to_bytes()`, `ntfs_get_locked_folio()`, and `ntfs_set_lcn_empty_bits()`. The inline public wrappers live in `bitmap.h`.

## Risks And Edge Cases

- `__ntfs_bitmap_set_bits_in_run()` does not explicitly special-case `count == 0`; `end_index = (start_bit + cnt - 1) >> ...` underflows for zero count.
- The rollback path can itself fail, in which case the volume is marked erroneous and metadata may remain inconsistent.
- The calls to `ntfs_set_lcn_empty_bits()` for partial first/final bytes pass a count but not an intra-byte start offset; this depends on that helper's interpretation of page/index state and should be reviewed.
- Trim's alignment can reduce a valid free cluster run to zero discarded bytes; this is intended, but tests need to cover `range->minlen` and discard granularity interactions.
- The bitmap folio is interpreted as `unsigned long *`, so bit order and machine word assumptions must match NTFS's on-disk little-endian bitmap semantics on supported architectures.

## Test Signals

Tests should set and clear bit ranges starting and ending at unaligned bits, crossing page boundaries, and spanning many pages; inject a later-page read failure to validate rollback; check `$Bitmap` free-space accounting updates; exercise fstrim over empty, full, and fragmented bitmaps; and validate discard range alignment and `range->len` reporting.
