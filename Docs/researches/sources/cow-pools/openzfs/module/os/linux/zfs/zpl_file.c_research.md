# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file.c

## Purpose
Provides Linux file and address-space operations for regular files and directories on ZFS. It adapts VFS open/read/write/fsync/mmap/writeback/fallocate/ioctl/fadvise/splice/range-copy callbacks to ZFS vnode/DMU operations.

## Main APIs and Data
- `zpl_file_operations` implements regular-file operations.
- `zpl_dir_file_operations` implements directory file operations.
- `zpl_address_space_operations` implements page-cache operations needed primarily for mmap.
- `zpl_open()`, `zpl_release()`, `zpl_iter_read()`, `zpl_iter_write()`, `zpl_fsync()`, `zpl_mmap()`, `zpl_writepages()`, and `zpl_fallocate()` are the core callbacks.
- Ioctl handlers expose Linux flags, xflags/project IDs, DOS flags, generation, and ZFS rewrite support.
- Tunable `zfs_fallocate_reserve_percent` controls legacy fallocate capacity reservation inflation.

## Control Flow
Open first runs `generic_file_open()` then calls `zfs_open()`. Release marks atime dirty inodes before `zfs_close()`. Readdir delegates to `zfs_readdir()`.

Read/write iterators build `zfs_uio_t` wrappers around Linux `iov_iter`, translate `kiocb` flags to ZFS-style `O_*` flags, call `zfs_read()` or `zfs_write()`, update file offset by residual count, and update access time with ZFS relatime awareness.

Fsync first pushes dirty mmap/page-cache pages into the DMU/ZIL using `zpl_write_cache_pages()` in non-sync mode with `for_sync` semantics, then calls `zfs_fsync()`. Writeback similarly writes dirty pages to the DMU, optionally commits the ZIL once for `WB_SYNC_ALL`, then performs a second pass because non-sync page collection may not catch every dirty page.

Mmap is intentionally double-cached: ARC remains ZFS’s primary cache while Linux page cache backs mapped VM pages. `readpage`/`read_folio` fills page-cache pages from ZFS, and `writepage`/`writepages` pushes mmap-dirtied pages back through `zfs_putpage()`.

Fallocate supports punch-hole and zero-range via `zfs_space(F_FREESP)`. Allocation mode is emulated with capacity checks and optional size extension because persistent preallocation conflicts with COW semantics.

Ioctl paths translate Linux immutable/append/nodump/projinherit and xflags to ZFS `z_pflags`/xattrs via `zfs_setattr()`, expose project IDs, support DOS attributes, and call `zfs_rewrite()` for rewrite requests.

## Integration Points
This file ties Linux VFS to `zfs_vnops`, `zfs_znode`, DMU prefetch/evict, ZIL commit, project quota-aware `zfs_statvfs()`, Linux page-cache compatibility wrappers, file range cloning declarations, ACL/xattr-related setattr behavior, and kernel ioctl ABIs.

## Invariants and Edge Cases
- Generic direct_IO should never be reached; the callback panics because direct I/O is handled by read/write iterators.
- `zpl_fsync()` returns early on page flush errors because a later ZIL commit may not surface them reliably.
- `ZFS_SYNC_ALWAYS` forces sync writeback behavior.
- O_DIRECT, O_SYNC, O_DSYNC, and append are derived from `kiocb` flags when available.
- Fallocate reserve percentage `0` disables allocation-mode emulation.
- Setting immutable/append requires `CAP_LINUX_IMMUTABLE`; flag updates require owner/capability checks.
- Compat ioctl only maps 32-bit get/set version/flags.

## Risks and Testing Signals
Important tests include mmap read/write/fsync consistency, writeback error propagation, syncfs/fsync under suspended pool, fallocate modes and quota/project quota interactions, direct I/O read/write, fadvise prefetch/evict, ioctl flag races, project ID set/get, DOS flags, and rewrite permission checks.
