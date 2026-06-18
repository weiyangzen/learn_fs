# sources/distributed-fs/ceph-client/fs/ntfs/file.c

Purpose: provides VFS regular-file, symlink, and special-inode operations for NTFS, including open/release, fsync, getattr/setattr, buffered/direct I/O, mmap, ioctl, and fallocate-style range operations.

Important APIs and functions:
- `ntfs_file_ops`, `ntfs_file_inode_ops`, `ntfs_symlink_inode_operations`, and `ntfs_special_inode_operations` are the exported VFS operation tables.
- `ntfs_file_open()` rejects shutdown volumes, checks 32-bit page-cache limits, and enables nowait/direct-I/O capability flags.
- `ntfs_trim_prealloc()` trims unused preallocated sparse holes on last close for non-compressed files.
- `ntfs_file_fsync()` persists file data, base and extent MFT records, named nonresident attributes, parent directory indexes, MFT bitmap, LCN bitmap, MFT, and block device cache.
- `ntfs_setattr()` handles truncation, chmod/chown timestamps, readonly flag updates, POSIX ACL chmod, and WSL EA metadata.
- `ntfs_file_read_iter()` and `ntfs_file_write_iter()` dispatch to iomap buffered/direct I/O and compressed writes.
- `ntfs_ioctl()` handles shutdown, get/set volume label, and FITRIM.
- `ntfs_fallocate()` supports allocate, keep-size, punch-hole, collapse-range, and insert-range modes.

Control flow:
- Write path rejects shutdown/encrypted writes and direct I/O to compressed files, locks the inode or returns `-EAGAIN` for NOWAIT, performs generic write checks, marks the volume dirty, snapshots sizes, and dispatches to compressed, direct, or buffered write helpers. On error it rolls initialized size and data size back.
- Direct writes use `iomap_dio_rw()` and may fall back to buffered writes for remaining bytes; fallback writes are synced and invalidated.
- Size setattr waits for DIO, updates VFS size, truncates NTFS attributes, rolls back on failure, and zeroes partial page gaps for nonresident extension.
- Fallocate maps the whole runlist if needed, marks the volume dirty, waits DIO, locks mapping invalidation for destructive modes, calls the mode-specific helper, then updates times, filename metadata, and dirty state.
- Hole punching zeroes unaligned edge clusters through iomap before deallocating full clusters.
- Collapse and insert require cluster-aligned offset/length and rewrite nonresident runlists through attribute helpers.

State and persistence behavior:
- Volume dirty flag is set before writes, setattr, and fallocate mutations.
- Release-time trim can change runlist, allocated size, and mapping pairs after application closes a file.
- `ntfs_getattr()` reports birth time, compressed/encrypted/immutable/append attributes, DIO alignment for eligible regular files, and includes pending deallocation clusters in block count.
- Fsync writes parent directory index allocation inodes for every filename hardlink, then flushes volume allocation metadata and block device cache.
- Symlink `get_link` returns the parsed `NTFS_I(inode)->target` generated during inode load.

Dependencies and integration points:
- Depends on `lcnalloc.h`, `ntfs.h`, `reparse.h`, `ea.h`, `iomap.h`, and `bitmap.h`.
- Uses iomap operation sets from NTFS iomap code for read/write/seek/page-mkwrite.
- Uses EA helpers for WSL uid/gid/mode metadata and listxattr/ACL inode hooks.
- Uses allocation helpers for cluster trim and FITRIM.
- Shares ioctl handlers with directory operations.

Risks and edge cases:
- `ntfs_file_write_iter()` error message checks `NInoEncrypted()` but prints compressed/encrypted based on `NInoCompressed()`, making compressed text unreachable in that branch.
- Release-time prealloc trim can fail after userspace close; errors from `.release` are often ignored by applications.
- Direct-I/O alignment requires superblock block size, while reported DIO alignment uses bdev logical block size; mismatches should be tested.
- `ntfs_dio_write_iter()` treats `-ENOTBLK` as partial fallback success; accounting around mixed direct/buffered writes is subtle.
- Fallocate waits indefinitely for free-cluster knowledge and returns `-ENOSPC` when the MFT zone length is zero, which can surprise callers unrelated to requested range.

Test signals:
- Exercise buffered/direct read/write, NOWAIT lock contention, compressed/encrypted rejection, partial direct-write fallback, mmap shared write initialization, and fsync metadata propagation.
- Test truncate extension over partial pages, shrink rollback, chmod/chown WSL EA updates, readonly DOS bit mapping, and POSIX ACL chmod.
- Fallocate tests should cover all supported modes, cluster alignment errors, sparse-disabled behavior, edge zeroing for punch-hole, and filename metadata updates.
- Ioctl tests should cover capability checks, volume-label copy bounds, FITRIM minlen/granularity, and shutdown gating.
