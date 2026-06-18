# sources/distributed-fs/ceph-client/fs/zonefs/file.c

## Purpose
`zonefs/file.c` implements zonefs file IO. It maps zone files to raw block device sectors through iomap, enforces sequential-zone append semantics, handles truncate-to-reset/finish operations, tracks write-open zones, and reacts to IO errors.

## Important APIs, types, and functions
Exports are `zonefs_file_aops`, `zonefs_file_operations`, and `zonefs_file_truncate`. Key helpers include read/write iomap begin functions, folio read/readahead/writeback operations, `zonefs_file_fsync`, mmap prepare/page_mkwrite, direct and buffered write paths, direct read completion, splice read, sequential write open/close, and file open/release.

## Control flow
Reads map written bytes as `IOMAP_MAPPED` and reads past EOF as holes. Conventional-zone writes can use buffered writeback and shared writable mmap. Sequential-zone writes must be direct, block-size aligned, and positioned at `z_wpoffset`; append writes rewrite `ki_pos` to the write pointer. The write path advances `z_wpoffset` before IO and completion grows inode size after successful direct IO; failures call `zonefs_io_error` to resync with hardware. Truncating sequential files to zero issues zone reset; truncating to capacity issues zone finish.

## State and persistence
Per-inode state is `i_truncate_mutex`, `i_wr_refcnt`, inode size, and `struct zonefs_zone` fields such as `z_wpoffset` and open/active flags. Persistent state is mostly the block device zone condition and write pointer; zonefs has no per-file metadata beyond the formatted superblock and in-memory zone table.

## Dependencies and integration points
It depends on iomap buffered/direct IO, block device flushes, zone management operations from `super.c`, VFS locks, mmap invalidate locks, swap activation, large folios, and tracepoints.

## Risks and test signals
Risks include sequential write reordering, async NOWAIT semantics, partial direct IO, stale `z_wpoffset` after errors, truncation races with mmap/read/write, explicit-open accounting leaks, full-zone close handling, and conventional writeback accidentally used on sequential zones. Test signals include direct append writes, misaligned writes, IOCB_NOWAIT, buffered conventional writes, mmap writes, reset/finish truncate, fsync, splice read, swapfile activation, and injected zone write errors.
