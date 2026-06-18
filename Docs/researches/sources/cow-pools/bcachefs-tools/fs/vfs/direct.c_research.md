# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/direct.c

Purpose: Direct IO read/write implementation for bcachefs VFS.

Key APIs and behavior:
- Direct reads validate 512-byte alignment, clamp to file size, build one or more bios from the iov_iter, and complete synchronously or asynchronously via closures.
- Direct read path flushes overlapping cached writes before issuing O_DIRECT.
- `bch2_read_iter()` dispatches direct reads or falls back to `filemap_read` under pagecache-add guard.
- Direct writes validate block alignment, perform generic write checks, invalidate overlapping pagecache, block pagecache additions, and use inode DIO lifetime references.
- Write loop maps user pages under faults-disabled mapping tracking, handles dropped pagecache locks, trims unaligned tails, reserves quota/disk space, and submits bcachefs writes.
- Async direct writes copy iovec state when continuation may outlive caller stack and use `kthread_use_mm()` for continuation mapping.
- Dsync writes optionally flush journal and nocow writes before completion.

Integration:
- Declared in `direct.h`.
- Uses VFS/pagecache helpers, bcachefs data read/write, quota/accounting, fault-disabled mapping table from `fdm.h`, and enumerated write refs.

Risks and invariants:
- Direct writes extending i_size are forced synchronous.
- Fault handler/pagecache invalidation interaction is delicate and signaled through `fdm_dropped_locks`.
- Async path must own copied iovecs before returning `-EIOCBQUEUED`.
