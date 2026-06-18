# sources/distributed-fs/ceph-client/fs/affs/inode.c

## Purpose
`inode.c` maps AFFS header blocks to Linux inodes, writes inode metadata back to disk, handles setattr/truncate, evicts inodes, allocates new header blocks, and creates directory entries.

## Important APIs, types, and functions
Public entry points are `affs_iget()`, `affs_write_inode()`, `affs_setattr()`, `affs_evict_inode()`, `affs_new_inode()`, and `affs_add_entry()`.

## Control flow
`affs_iget()` reads and checksums a header block, interprets the tail stype, converts protection/UID/GID/time, initializes extension/preallocation caches, and installs file, directory, or symlink operations. `affs_write_inode()` updates tail protection, size, timestamps, UID/GID, root change time, checksums, and metadata buffers. `affs_setattr()` validates option-controlled permission changes and calls `affs_truncate()` for size changes. `affs_add_entry()` initializes a file/dir/link/symlink header and inserts it into the target directory hash.

## State and persistence
It initializes per-inode runtime caches and writes persistent header tails: mode/protection, size, UID/GID, timestamps, names, parents, link chains, and stype.

## Dependencies and integration points
It integrates with bitmap allocation/free, file truncation, namei operations, symlink aops, metadata buffer tracking, and mount flags such as `setuid`, `setgid`, `mode`, `mufs`, `ofs`, and `protect`.

## Risks and test signals
Risks include bad inode acceptance, UID/GID MUFS translation errors, mode override behavior, link-chain nlink approximation, dirty metadata ordering, and freeing header blocks on eviction. Test signals include iget for root/files/dirs/symlinks, chmod/chown under mount policies, create/link/symlink entry creation, truncate on setattr, eviction of unlinked files, and writeback checksum validation.
