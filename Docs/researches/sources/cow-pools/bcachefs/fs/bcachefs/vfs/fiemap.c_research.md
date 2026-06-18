# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fiemap.c

## Summary
Implements bcachefs FIEMAP support by merging extent-btree mappings with dirty pagecache holes and reporting physical, inline, shared, encoded, unwritten, delalloc, and alignment flags.

## Main Responsibilities
- Converts bcachefs extent keys into FIEMAP records.
- Reports direct data pointers, inline data, reservations/delalloc, and skips error keys.
- Scans pagecache holes to synthesize delayed-allocation extents for dirty cached data.
- Handles reflink pointer resolution through `bch2_read_indirect_extent()`.
- Iterates the requested file range under btree transactions and emits extents in order.
- Marks the final emitted extent with `FIEMAP_EXTENT_LAST`.

## Key APIs
- `bch2_fiemap()`.

## Important Behavior
`bch2_fill_extent()` reports each decoded direct-data pointer. Reflink-value extents are marked shared. Compressed extents are marked encoded; uncompressed physical offsets include CRC offset. Unaligned physical offsets or sizes get `FIEMAP_EXTENT_NOT_ALIGNED`.

For holes in the extent btree, the code scans pagecache for data and fabricates an extent key with a dummy pointer and `FIEMAP_EXTENT_DELALLOC`. It first tries a nonblocking scan while holding btree locks, then drops locks for a blocking scan on `-EAGAIN`.

## Risks
The file documents a semantic compromise: pagecache should take precedence for COW dirty data, but without per-sector writeback tracking this can over-report delalloc for clean cached data. FIEMAP mappings are not stable because bcachefs background relocation can move data after reporting.
