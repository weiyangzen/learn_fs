# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/nilfs.h

## Purpose

Primary NILFS local header defining in-memory inode state, transaction state, inode number classification, flag helpers, exported cross-file function prototypes, logging macros, and operation table declarations.

## Main Structures and State

- `struct nilfs_inode_info`
  - Embeds VFS inode and stores NILFS-specific flags, inode type, dynamic state bits, bmap storage, xattr placeholder, directory lookup hint, checkpoint number for GC inodes, associated inode pointer, dirty-list node, inode buffer, and root pointer.
- `struct nilfs_transaction_info`
  - Tracks per-task NILFS transaction context through `current->journal_info`, including magic, saved journal info, flags, and nesting count.

## Important Enums and Flags

- Dynamic inode state bits:
  - `NILFS_I_NEW`
  - `NILFS_I_DIRTY`
  - `NILFS_I_QUEUED`
  - `NILFS_I_BUSY`
  - `NILFS_I_COLLECTED`
  - `NILFS_I_UPDATED`
  - `NILFS_I_INODE_SYNC`
  - `NILFS_I_BMAP`
- In-memory inode types:
  - normal
  - GC
  - btree node cache
  - shadow
- Transaction flags:
  - dynamic allocation
  - sync
  - GC
  - commit
  - writer

## Main Helpers

- `NILFS_I()` converts VFS inode to NILFS inode info.
- `NILFS_BMAP_I()` converts bmap pointer to NILFS inode info.
- Inode number macros classify metadata, system, valid, and private inodes.
- `nilfs_set_transaction_flag()`, `nilfs_test_transaction_flag()`, `nilfs_doing_gc()`, and `nilfs_doing_construction()` inspect transaction context.
- `nilfs_init_acl()` is a stub when POSIX ACL is disabled and applies current umask for non-symlinks.
- `nilfs_mask_flags()` filters inode flags by file type.
- `nilfs_mark_inode_dirty()` and `nilfs_mark_inode_dirty_sync()` wrap `__nilfs_mark_inode_dirty()` with VFS dirty flags.

## API Surface Declared

- Directory helpers and file sync.
- Ioctl and cleaner preparation.
- Inode lifecycle, block mapping, truncation, dirtying, permission, and FIEMAP.
- Superblock read/commit/checkpoint/resize helpers.
- GC inode cache helpers.
- Sysfs group management.
- VFS operation tables and filesystem type.

## Dependencies and Interactions

- Includes Linux buffer/block headers, NILFS UAPI and on-disk format headers, `the_nilfs.h`, and `bmap.h`.
- Included widely across this group; it is the shared contract between `inode.c`, `namei.c`, `ioctl.c`, `mdt.c`, `page.c`, `recovery.c`, and segment construction code.
