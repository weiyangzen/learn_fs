# sources/distributed-fs/ceph-client/fs/affs/file.c

## Purpose
`file.c` implements AFFS regular-file I/O, logical-to-physical block mapping, extension-block caches, OFS data-block handling, truncation, preallocation cleanup, fsync, and VFS file/address-space operation tables.

## Important APIs, types, and functions
Key functions include `affs_get_block()`, `affs_get_extblock_slow()`, `affs_alloc_extblock()`, `affs_grow_extcache()`, `affs_read_folio()`, `affs_write_begin()`, `affs_write_end()`, `affs_direct_IO()`, OFS variants `affs_read_folio_ofs()`, `affs_write_begin_ofs()`, `affs_write_end_ofs()`, `affs_extent_file_ofs()`, plus `affs_free_prealloc()`, `affs_truncate()`, and `affs_file_fsync()`.

## Control flow
FFS paths use buffer-head block mapping: logical blocks select an extension block, allocate missing extension/data blocks when creating, update header tables/checksums, and use generic buffered/direct I/O helpers. OFS paths account for 24-byte data headers, copy payload data between folios and `AFFS_DATA()`, maintain `next` links, sequence numbers, sizes, and checksums. File release truncates if `i_size` differs from `mmu_private` and frees preallocations. Truncate frees data and extension blocks beyond the new EOF.

## State and persistence
Runtime state includes extension linear/associative caches, cached extension buffer, block counts, extension counts, `mmu_private`, last allocation, and preallocation count. Persistent state includes data block pointers, extension chains, OFS data headers, first-data pointers, checksums, and archived protection bit clearing.

## Dependencies and integration points
It depends on bitmap allocation, metadata buffer tracking, VFS writeback/mpage/direct I/O helpers, `affs.h` block macros, and inode dirtying.

## Risks and test signals
Risks include extension-cache stale entries, checksum delta mistakes, partial-write OFS consistency, preallocation leaks, sparse/growing file edge cases, direct I/O beyond `mmu_private`, and truncate freeing wrong chains. Test signals include FFS and OFS read/write, append, hole extension, short writes, direct I/O fallback, large files spanning many extensions, close-time truncate, fsync, ENOSPC, and archived-bit clearing.
