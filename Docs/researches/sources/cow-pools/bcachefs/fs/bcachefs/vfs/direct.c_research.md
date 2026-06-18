# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/direct.c

## Summary
Implements bcachefs direct I/O read and write paths plus the VFS `read_iter` dispatcher.

## Main Responsibilities
- Performs aligned O_DIRECT reads into user-backed iterator pages.
- Supports sync and async direct-read completion through closures.
- Flushes overlapping pagecache before direct reads.
- Performs aligned O_DIRECT writes with pagecache invalidation/blocking.
- Handles async direct-write continuation after each write operation.
- Reserves quota and disk space, checks whether existing allocated extents can satisfy writes, and accounts inode sectors.
- Handles extending writes, dsync flushes, and inode direct-I/O lifetime.
- Detects and handles page faults that dropped pagecache locks via FDM tracking.

## Key APIs
- `bch2_direct_IO_read()`.
- `bch2_read_iter()`.
- `bch2_direct_write()`.

## Important Behavior
Direct reads require sector alignment, trim reads to EOF, shorten the iterator to a block-aligned size for the lower read path, and dirty user pages unless the iterator is kernel/internal backed.

Direct writes require filesystem block alignment. Extending writes remain inode-locked and force sync behavior so `i_size` is updated safely. Non-extending writes can drop the inode lock after setting up direct-I/O and pagecache blocking.

The write loop fills bios from the iterator, invalidates pagecache again if a page fault dropped locks, trims unaligned tail bytes, initializes a `bch_write_op`, reserves quota/disk space, submits the write, and either continues asynchronously or loops synchronously.

## Risks
Direct I/O interlocks with page faults, mmap/pagecache invalidation, quotas, disk reservations, journal flushing, and async callback lifetime. Async writes may need to copy iovecs because caller stack storage can disappear after returning `-EIOCBQUEUED`. The FDM dropped-lock path is subtle and must re-invalidate before using newly pinned pages.
