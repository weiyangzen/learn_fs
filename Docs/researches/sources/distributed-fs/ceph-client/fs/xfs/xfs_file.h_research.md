# sources/distributed-fs/ceph-client/fs/xfs/xfs_file.h

## Purpose
`xfs_file.h` exposes XFS regular-file and directory VFS operation tables and a shared fallocate alignment helper.

## Important APIs, types, and functions
It declares `xfs_file_operations`, `xfs_dir_file_operations`, and `xfs_is_falloc_aligned`.

## Control flow
Mount/inode setup code uses the operation tables for regular files and directories. Fallocate and exchange-range related code can call the alignment helper before extent-moving operations.

## State and persistence
The header has no state. The declared operation tables drive all persistent file data and metadata changes implemented in `xfs_file.c`.

## Dependencies and integration points
It depends on VFS `struct file_operations` and XFS inode types and is included by file-operation implementation and inode setup paths.

## Risks and test signals
Risk is minimal; changes here alter the public internal contract for VFS integration. Test signals are build coverage and mount-time assignment of file and directory operations.
