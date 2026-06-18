# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.c

Implements VFS-level file I/O helpers around fsync, truncate, fallocate, hole punching, collapse/insert range, reflink/remap, quota/disk accounting, nocow flushes, and `llseek(SEEK_DATA/SEEK_HOLE)`.

Key entry points:
- `bch2_inode_flush_nocow_writes_async()` and `bch2_fsync()` flush pagecache, inode metadata, journal sequence, and devices that received nocow writes.
- `bch2_write_inode_size()` writes size and selected time fields to the btree inode.
- `__bch2_i_sectors_acct()` / `bch2_i_sectors_acct()` update `i_blocks`, quota reservations, and quota accounting.
- `bch2_zero_pagecache_posteof()` and `bchfs_truncate()` implement size changes and post-EOF zeroing.
- `bch2_fallocate_dispatch()` dispatches normal preallocation, zero range, punch hole, insert range, and collapse range.
- `bch2_remap_file_range()` implements clone/dedupe-style remapping between files.
- `bch2_llseek()` implements regular seek plus btree/pagecache-aware `SEEK_DATA` and `SEEK_HOLE`.

Core mechanics:
- Nocow write flushing consumes `inode->ei_devs_need_flush`, submits `REQ_PREFLUSH` bios through `nocow_flush_bioset`, and holds per-device write refs until endio.
- `bch2_flush_inode()` reads the authoritative inode journal sequence from the btree, repairs impossible future sequence values, flushes the journal to that sequence, then flushes nocow devices.
- Truncation blocks concurrent pagecache additions, waits for DIO, reads the btree inode, handles journal error cases, truncates partial folios, updates VFS size, flushes straddling/extended ranges, calls btree truncate, adjusts `i_blocks`, and writes final attributes.
- Partial folio truncation reads existing data when needed, initializes `bch_folio` sector state, marks full filesystem-block sectors unallocated, zeroes the requested bytes, obtains a nofail disk reservation to avoid truncate `ENOSPC`, cleans writable mappings, and redirties the folio.
- Fallocate walks extent slots in the target subvolume, skips already-reserved data, clamps holes against dirty pagecache, reserves quota/disk space, installs extent reservations, marks pagecache sectors reserved, and updates block accounting.
- Remap validates flags/alignment/overlap, locks both files, blocks pagecache additions, waits for DIO, prepares the generic remap, invalidates destination pagecache, reserves quota for destination holes, updates source pagecache allocation state, calls `bch2_remap_range()`, updates destination `i_size`, and flushes when sync semantics require it.
- `SEEK_DATA` and `SEEK_HOLE` combine extent btree scans with pagecache state so dirty cached data not yet in the btree is visible to userspace.

Important invariants:
- Size-changing operations hold `i_rwsem` via VFS callers or explicitly lock the inode, wait for DIO, and use `bch2_pagecache_block` when invalidating or restructuring cached pages.
- `i_blocks` underflow is treated as a filesystem check error and clamped to prevent negative VFS state.
- Truncate may set `EI_INODE_ERROR` when btree truncate fails after VFS pagecache/size state changed.
- Fallocate and remap must release quota reservations on all error paths.
- Collapse/insert range require block-size alignment and invalidate/write back all affected pagecache before btree extent movement.

Filesystem relevance:
- This is the bcachefs VFS file-space mutation layer. It coordinates user-visible file size/range operations with extent btrees, quota accounting, pagecache state, journal durability, and copy-on-write/reflink semantics.

Notable risks:
- Comments note that partial-folio truncate currently cannot distinguish real data from zero-only content precisely.
- Pagecache invalidation can spin if another task repeatedly redirties a page.
- Remap aligns the btree operation beyond the requested byte length, then trims the reported byte count back to the user-requested range.
