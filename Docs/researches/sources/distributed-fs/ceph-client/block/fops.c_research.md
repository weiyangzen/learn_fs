<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/fops.c -->
# sources/distributed-fs/ceph-client/block/fops.c

## Purpose
`fops.c` implements the generic block-device `struct file_operations` and default address-space operations for block special files. It is the bridge between VFS reads/writes/mmap/fsync/fallocate/ioctl/io_uring and block-device primitives such as bios, page cache invalidation, cache writeback, flushes, zeroing, and open-mode conversion.

## Important APIs, Types, and Functions
- `def_blk_fops` wires block devices into VFS: `blkdev_open`, `blkdev_release`, `blkdev_read_iter`, `blkdev_write_iter`, `blkdev_llseek`, `blkdev_fsync`, `blkdev_fallocate`, `blkdev_mmap_prepare`, `blkdev_ioctl`, `compat_blkdev_ioctl`, and `blkdev_uring_cmd`.
- `def_blk_aops` is compiled in two variants. With `CONFIG_BUFFER_HEAD`, it uses buffer-head helpers (`block_read_full_folio`, `block_write_full_folio`, `mpage_readahead`). Without buffer heads, it uses iomap helpers (`iomap_bio_read_folio`, `iomap_writepages`).
- `struct blkdev_dio` stores direct-I/O state shared by bios: original `kiocb` or sync waiter, total size, reference count, flags, and an embedded first `bio` allocated from `blkdev_dio_pool`.
- Direct-I/O helpers include `blkdev_direct_IO`, `__blkdev_direct_IO_simple`, `__blkdev_direct_IO_async`, `__blkdev_direct_IO`, `blkdev_bio_end_io`, and `blkdev_bio_end_io_async`.
- `file_to_blk_mode()` converts file flags and modes into block open flags, including historical `O_RDWR | O_WRONLY` write-ioctl behavior.

## Control Flow
Open starts in `blkdev_open()`: file flags become `BLK_OPEN_*` flags, exclusive opens set `file->private_data`, permissions are checked via `bdev_permission()`, the bdev is looked up with `blkdev_get_no_open()`, metadata and atomic-write capabilities are reflected in `f_mode`, then `bdev_open()` owns the live reference. Release delegates to `bdev_release()`.

Reads in `blkdev_read_iter()` trim the iterator at device end, optionally do direct I/O after waiting for conflicting writeback, then fall back to `filemap_read()` under the block inode shared lock. Writes in `blkdev_write_iter()` reject read-only devices, swapfile writes, NOWAIT-buffered writes, writes beyond end, and invalid atomic writes. They trim to device size, update mtime/ctime, run direct I/O when requested, and can fall back to buffered iomap writes for short direct writes.

Direct I/O is selected by mapping size and metadata needs. Small, synchronous, single-bio I/O uses `submit_bio_wait()`. Async single-bio I/O can queue `REQ_POLLED`, `REQ_NOWAIT`, `REQ_ATOMIC`, integrity metadata, write streams, and ioprio. Multi-bio I/O uses `blkdev_dio` refcounts and completion coalescing.

## State and Persistence Behavior
The file persists no independent on-disk metadata, but it mutates durable media through writes, zeroing, flushes, and fallocate. It also changes in-memory page-cache state aggressively: direct writes invalidate before and after I/O, fallocate invalidates dirty cache for deallocation/zeroing, fsync writes cached data and issues a block flush, and read/write paths coordinate with block-size changes via inode locks.

## Dependencies and Integration Points
The file depends on VFS, iomap, buffer-head or non-buffer-head address-space operations, bio allocation/submission, integrity metadata mapping, task I/O accounting, suspend hibernation checks, and block-device open/close helpers from `blk.h`. It exports no symbols itself, but `def_blk_fops`, `def_blk_aops`, and `file_to_blk_mode()` are central block-layer integration surfaces.

## Risks and Edge Cases
Alignment is strict for direct I/O and fallocate: misaligned offsets/counts return `-EINVAL`. NOWAIT support is intentionally limited when multiple bios would be needed. Completion ordering and `ki_pos` updates are split between direct-I/O helper variants, so regressions can double-advance offsets or leak `iocb->private`. Buffered paths rely on inode locks to avoid races with `set_blocksize()`. Device-size truncation, atomic-write short writes, and metadata mapping failures are high-risk behavior.

## Test Signals
Useful tests include xfstests block-device direct/buffered read-write cases, O_DIRECT alignment failures, io_uring polled direct I/O, integrity metadata I/O, write stream validation, fsync flush behavior on devices without flush support, fallocate zero/punch/write-zeroes modes, read/write at end-of-device, and lockdep runs around block-size changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/fops.c -->
