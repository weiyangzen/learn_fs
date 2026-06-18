# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/buffered.c

## Summary
Implements bcachefs buffered VFS I/O: readahead, single-folio reads, writeback, write_begin/write_end, multi-folio buffered writes, and the buffered branch of `write_iter`.

## Main Responsibilities
- Converts readahead folios into read bios and submits extent reads.
- Extends read bios across adjacent folios and can opportunistically allocate more folios for expensive partial reads.
- Reads a single folio synchronously for pagecache misses and partial-write preparation.
- Builds writeback bios from dirty folio-sector state and submits bcachefs write operations.
- Handles writeback throttling on allocator and journal pressure.
- Manages folio disk reservations for buffered writes.
- Handles EOF-straddling folios, post-EOF zeroing, short writes, pagecache cleanup, dirtying, and inode size updates.
- Routes `bch2_write_iter()` between direct and buffered paths.

## Key APIs
- `bch2_readahead()`.
- `bch2_read_single_folio()`, `bch2_read_folio()`.
- `bch2_writepages()`.
- `bch2_write_begin()`, `bch2_write_end()`.
- `bch2_write_iter()`.

## Important Behavior
`bchfs_read()` walks the extents btree for an inode/subvolume snapshot, resolves indirect/reflink extents, sets page state from the extent, and calls the lower read path. It temporarily narrows the bio size to an extent fragment and either submits the last fragment directly or clones for earlier fragments.

Writeback snapshots each folio’s sector reservations under the folio-state spinlock before unlocking the folio. It updates per-sector states to allocated, clears reservations, starts writeback, and batches contiguous dirty sectors into `bch_writepage_io`.

Buffered writes lock contiguous folios, read boundary folios when required, reserve sectors, copy from the user iterator atomically, mark successful ranges uptodate/dirty, and update `i_size`.

## Risks
This path is tightly coupled to folio-private state, btree transaction locking, extent semantics, disk reservations, and writeback lifetime. The read path explicitly warns that transaction restarts after `bch2_read_extent()` would be dangerous because the rbio iterator may already have been handed off. Partial writes and reservation failures must preserve pagecache and iterator consistency.
