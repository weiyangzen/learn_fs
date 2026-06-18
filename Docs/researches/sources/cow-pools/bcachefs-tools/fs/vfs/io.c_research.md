# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/io.c

Purpose: implements higher-level file I/O operations around fsync, truncate, fallocate, remap/dedupe, nocow flushes, i_size updates, quota accounting, and `llseek` data/hole behavior.

Key behavior:
- Issues asynchronous prefush bios for devices touched by nocow writes, then integrates that into fsync.
- `bch2_fsync()` waits dirty file data, syncs inode metadata, flushes journal sequence, flushes nocow writes, checks writeback errors, and emits trace data.
- `bchfs_truncate()` coordinates DIO waits, pagecache blocking, partial-folio zeroing, pagecache truncation, btree truncation, i_blocks accounting, reserved-range invalidation, and final inode metadata update.
- Fallocate supports regular allocation, zero range, punch hole, insert range, and collapse range.
- Remap/dedupe validates flags/alignment/overlap, blocks pagecache, invalidates destination pages, reserves quota, remaps btree extents, adjusts i_size, and optionally flushes sync destinations.
- `bch2_llseek()` supports normal seeks plus `SEEK_DATA`/`SEEK_HOLE`, combining extent btree state with dirty pagecache scans.

Important interactions:
- Relies on pagecache helpers for folio truncation, reservation marking, pagecache hole/data scanning, and write-invalidate loops.
- Uses `bch2_i_sectors_acct()` to keep VFS `i_blocks`, quota reservation, and quota accounting aligned.
- Uses per-inode cached reservation ranges from `fs.h`; operations that mutate extent layout clear the cache.
- Most mutating paths check read-only state or acquire internal write refs.
