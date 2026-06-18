<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/file.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/file.c

## Purpose

`file.c` is the main VFS-facing regular-file implementation for F2FS. It provides the `f2fs_file_operations` and `f2fs_file_inode_operations` tables, plus the implementation behind mmap faults, fsync, llseek with `SEEK_DATA`/`SEEK_HOLE`, open/release/flush, fallocate range operations, ioctls, direct and buffered read/write iterators, file attributes, project quota changes, pinned-file control, compression management, secure trim, and advisory behavior. The file is also a coordination point between page cache state, node/data block mappings, checkpoints, roll-forward recovery, quota, fscrypt, fsverity, compression, GC, and multi-device/zoned-device constraints.

## Important APIs, Types, and Functions

- `f2fs_file_operations` wires the VFS file surface: `llseek`, `read_iter`, `write_iter`, `iopoll`, `open`, `release`, `mmap_prepare`, `flush`, `fsync`, `fallocate`, ioctls, splice, fadvise, and lease support.
- `f2fs_file_inode_operations` provides file inode methods: `getattr`, `setattr`, ACL operations, xattrs, fiemap, and fileattr get/set.
- `f2fs_do_sync_file()` and `f2fs_sync_file()` implement F2FS fsync/fdatasync policy. They choose between checkpoint-based consistency and roll-forward node persistence using inode flags, written-data ino lists, parent inode state, compression, hardlinks, strict fsync mode, and barrier flushing.
- `f2fs_vm_page_mkwrite()` handles writable mmap faults. It converts inline data, allocates or looks up blocks, rejects unsupported large-folio writable mappings, waits on data and GC writeback, zeros partial EOF, and marks the folio dirty.
- `f2fs_llseek()` and `f2fs_seek_block()` implement `SEEK_DATA` and `SEEK_HOLE`, including inline-data and compressed-cluster handling.
- Truncation and range manipulation are split across `f2fs_truncate_data_blocks_range()`, `f2fs_do_truncate_blocks()`, `f2fs_truncate_blocks()`, `f2fs_truncate()`, `f2fs_truncate_hole()`, `f2fs_punch_hole()`, `f2fs_collapse_range()`, `f2fs_zero_range()`, `f2fs_insert_range()`, and `f2fs_expand_inode_data()`.
- Block exchange helpers `__read_out_blkaddrs()`, `__clone_blkaddrs()`, `__exchange_data_block()`, and rollback logic support collapse/insert/move-range semantics and handle checkpointed versus non-checkpointed blocks.
- `f2fs_fallocate()` validates supported modes and dispatches to punch, collapse, zero, insert, or preallocation paths.
- `__f2fs_ioctl()` dispatches F2FS and generic fs ioctls for atomic write, shutdown, trim, encryption keys/policies, GC, checkpoint, defrag, move range, flush device, features, pinning, resize, verity, labels, compression block accounting, secure trim, compression options, full-file compress/decompress, device alias detection, and IO priority.
- `f2fs_file_read_iter()`, `f2fs_file_splice_read()`, `f2fs_file_write_iter()`, `f2fs_dio_read_iter()`, `f2fs_dio_write_iter()`, and `f2fs_buffered_write_iter()` provide the hot data I/O path.
- `f2fs_should_use_dio()` centralizes direct-I/O eligibility. `f2fs_force_buffered_io()` rejects DIO for unsupported encryption, verity, compression, inline reads, unaligned multi-device layouts, zoned writes that are not pinned, and checkpoint-disabled mode.
- Compression management includes `release_compress_blocks()`, `reserve_compress_blocks()`, `f2fs_release_compress_blocks()`, `f2fs_reserve_compress_blocks()`, `f2fs_ioc_compress_file()`, `f2fs_ioc_decompress_file()`, option get/set, and compressed block count retrieval.

## Control Flow and State Behavior

The fsync path first writes dirty file data with possible in-place-update hints for fdatasync or small dirty ranges. It then decides whether a checkpoint is required through `need_do_checkpoint()`. Non-regular files, compressed files, hardlinks, superblock checkpoint demand, wrong parent inode, lack of roll-forward space, uncheckpointed parent nodes, fastboot, strict recovery of parent dentries, and xattr-dir writes force checkpointing. Otherwise, `f2fs_fsync_node_pages()` persists node pages for roll-forward recovery, optionally using atomic ordering. On success it removes the inode from APPEND/UPDATE/FLUSH ino tracking and may issue a flush unless nobarrier mode or atomic ordering avoids it.

Writable mmap faults follow a block-mapping path separate from normal write iterators. The code rejects immutable files and writable large-folio mappings, checks checkpoint readiness and compression backend readiness, converts inline data, optionally balances free space before allocation, locks the page-cache invalidation range, verifies the folio still belongs to the inode, allocates or validates the data block, waits for folio and GC-meta writeback, zeros EOF tail if needed, and dirties the folio. Pinned files do not allocate in this path; they require an existing valid block.

Truncation walks dnodes from the first freed block, clears data block addresses, batches contiguous invalidations, updates compressed-block counts, invalidates extent cache ranges, decrements valid block counts, and zeros the partial page at the new EOF. Compressed files are truncated at cluster boundaries and may need partial-cluster cleanup. Inline data is handled by clearing bytes directly in the inode page. Device-aliasing inodes use extent information and reject partial truncation.

Fallocate and move-range operations serialize with `inode_lock()`, direct-I/O completion, `i_gc_rwsem`, `filemap_invalidate_lock()`, and `f2fs_lock_op()` as needed. Full-block hole punching and zeroing alter dnode block addresses; partial pages are zero-filled through page cache. Collapse and insert exchange block mappings within the same file, while move-range can exchange blocks between two regular files on the same mount and superblock if unencrypted, uncompressed, unpinned, and block-aligned.

Read/write iterators choose direct versus buffered I/O per request. Direct reads increment `F2FS_DIO_READ`, hold `i_gc_rwsem[READ]`, and use iomap. Direct writes may also hold `i_gc_rwsem[READ]` in LFS/out-of-place mode, convert inline data, preallocate when useful, submit via iomap with F2FS write hints, update size on extension, and fall back to buffered write for partial direct I/O. Buffered writes go through `generic_perform_write()`. Failed or short preallocation is cleaned by truncating blocks beyond `i_size`.

Atomic write ioctls create or reuse a COW tmpfile inode, write back dirty pages, store original size, optionally truncate the visible inode for atomic replace, and commit through `f2fs_commit_atomic_write()` followed by an atomic fsync. Abort paths are called from explicit ioctl, release, and flush-on-exiting-owner.

## Persistence, Locking, and Integration Points

This file persists state through inode node pages, dnode block addresses, SIT valid-block counts, extent caches, superblock fields, checkpoint/roll-forward inode lists, quota files, compression counters, and on-disk inode flags. It uses `f2fs_lock_op()` for filesystem metadata transactions, `i_gc_rwsem[READ/WRITE]` to coordinate with GC and DIO, `filemap_invalidate_lock()` to protect page-cache invalidation, `inode_dio_wait()` before block removal, and mount write references for mutating ioctls.

Major dependencies are `f2fs.h`, `node.h`, `segment.h`, `xattr.h`, `acl.h`, `gc.h`, `iostat.h`, VFS helpers, iomap, fscrypt, fsverity, quota, block discard/zeroout, compression backends, and F2FS tracepoints. User-visible ioctl constants come from `uapi/linux/f2fs.h`. GC integration is explicit through `f2fs_gc()`, `gc_lock`, `f2fs_gc_range()`, pinned file state, and flush-device relocation.

## Risks and Edge Cases

High-risk areas are ordering and rollback around fsync, direct-write fallback, block exchange, compressed-cluster accounting, and ioctls that mutate filesystem-wide metadata. The code is defensive about checkpoint errors, checkpoint-disabled mode, unsupported compression backends, immutable/append-only restrictions, pinned-file alignment, device aliasing, malformed block addresses, and interrupted long operations. Several partial-progress compression operations can set `SBI_NEED_FSCK` if reservation or release only partly succeeds. Direct I/O has subtle compatibility rules: some O_DIRECT requests intentionally fall back to buffered I/O, then flush and invalidate the page cache to preserve expected semantics.

## Test Signals

Useful tests include xfstests-style coverage for fsync recovery, fdatasync, strict/nobarrier modes, mmap write faults, inline-to-block conversion, truncation around EOF, fallocate punch/collapse/zero/insert, DIO alignment fallback, O_DIRECT partial write fallback, encrypted/verity/compressed exclusions, atomic write commit/abort/recovery, project quota transfer, GC and GC-range ioctls, resize refusal paths, secure trim on single and multi-device filesystems, pinned file behavior on zoned and non-zoned devices, and full-file compression/decompression interrupted by signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/file.c -->
