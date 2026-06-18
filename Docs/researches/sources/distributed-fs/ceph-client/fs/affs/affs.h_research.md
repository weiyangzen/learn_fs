# sources/distributed-fs/ceph-client/fs/affs/affs.h

## Purpose
`affs.h` is the private interface for the AFFS driver. It defines in-memory inode/superblock structures, mount flags, block/tail access macros, function declarations, operation-table exports, checksum helpers, and locking wrappers.

## Important APIs, types, and functions
Important types are `struct affs_inode_info`, `struct affs_bm_info`, `struct affs_sb_info`, and `struct affs_ext_key`. Key macros are `AFFS_HEAD`, `AFFS_TAIL`, `AFFS_ROOT_HEAD`, `AFFS_ROOT_TAIL`, `AFFS_DATA_HEAD`, `AFFS_BLOCK`, and mount flag helpers. Inline helpers validate block ranges, read/get/zero/get-empty blocks, adjust checksums, release buffer_heads, and lock link, directory/hash, and extension state.

## Control flow
Most AFFS source files include this header and use it to interpret on-disk blocks as header/tail/data structures. VFS operations call functions declared here across source-file boundaries, while locking helpers serialize directory hash chains, hard-link chains, and extension-block caches.

## State and persistence
`affs_inode_info` persists runtime state such as open count, extension caches, metadata buffer tracking, preallocation, `mmu_private`, protection bits, and cached extension buffer. `affs_sb_info` stores mount policy, root block, bitmap cache, symlink prefix/volume, delayed superblock work, and root buffer.

## Dependencies and integration points
The header integrates AFFS with VFS inodes, buffer_heads, metadata buffer tracking, workqueues, mutexes, spinlocks, and Amiga on-disk structures from `amigaffs.h`.

## Risks and test signals
Risks include macro offset mistakes, checksum delta errors, invalid block-boundary assumptions, lock-order inversions, and stale declarations. Test signals include sparse/build coverage, lockdep under create/unlink/rename/write, invalid block reads, and checksum validation after metadata mutation.
