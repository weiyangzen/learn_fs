# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/types.h

Purpose: defines filesystem-wide VFS state embedded in `struct bch_fs`.

Key contents:
- `struct bch_fs_vfs` contains:
  - active inode fast list,
  - inode hash tables,
  - biosets for writepage, direct write, direct read, and nocow flush,
  - writepage buffer mempool,
  - delayed writeback workqueue.

Important interactions:
- Initialized and destroyed by `bch2_fs_vfs_init()`, `bch2_fs_vfs_init_rw()`, and `bch2_fs_vfs_exit()` in `fs.c`.
- Used by VFS inode tracking, direct I/O, writeback, and nocow flush paths.
