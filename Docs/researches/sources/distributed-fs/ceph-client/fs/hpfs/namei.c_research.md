# sources/distributed-fs/ceph-client/fs/hpfs/namei.c

Purpose: this file implements HPFS namespace mutation operations: mkdir, create, mknod, symlink, unlink, rmdir, symlink read, and rename.

Important APIs and functions: `hpfs_mkdir()`, `hpfs_create()`, `hpfs_mknod()`, `hpfs_symlink()`, `hpfs_unlink()`, `hpfs_rmdir()`, `hpfs_rename()`, and `hpfs_symlink_read_folio()` back the exported `hpfs_dir_iops` and `hpfs_symlink_aops`. `hpfs_update_directory_times()` updates parent directory timestamps and writes metadata immediately.

Control flow: create-like operations validate names, take `hpfs_lock()`, allocate fnodes and sometimes dnodes, prepare a dirent, create and initialize a VFS inode, insert the dirent into the parent dnode tree, fill fnode fields, write EAs if needed, insert the inode into the hash, update parent times, and instantiate the dentry. Error paths unwind allocated fnodes/dnodes and inodes. Unlink/rmdir locate the dirent, reject sentinel or wrong-type entries, remove from the dnode tree, update link counts, and update directory times. Rename validates flags/names, handles overwrite of non-directory targets, copies old dirent metadata with the new name/hidden flag, inserts/removes dirents as needed, updates parent directory link counts for moved directories, and rewrites the fnode parent/name fields.

State and persistence: namespace operations mutate directory dnode trees, fnodes, bitmap allocation, directory and file timestamps, link counts, symlink EAs, and inode parent tracking. Symlink targets are stored as the `SYMLINK` EA and read through the symlink address-space operation.

Dependencies and integration: it depends on allocation, dnode add/remove, inode initialization/writeback, EA writing/reading, name validation, and global locking. VFS exclusion is assumed for rename ordering.

Risks: many operations can fail after partial allocation, so unwind correctness is critical. Special files and symlinks require `sb_eas >= 2`; otherwise they return `-EPERM`. Rename over directories is rejected even though comments mention empty non-busy directories. Directory tree removal can return `2` for ENOSPC during delete rebalancing.

Test signals: create files/directories under ENOSPC, duplicate names, read-only mode bits, hidden dot names, special files and symlinks with EAs disabled/enabled, unlink and rmdir empty/non-empty dirs, rename within and across directories, overwrite non-directory targets, invalid rename flags, symlink page read, link-count updates, and fsck after mutation sequences.
