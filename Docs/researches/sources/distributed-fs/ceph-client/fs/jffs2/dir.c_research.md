# sources/distributed-fs/ceph-client/fs/jffs2/dir.c

## Purpose
`dir.c` implements JFFS2 directory file operations and inode operations: lookup, readdir, create, link, unlink, symlink, mkdir, rmdir, mknod, and rename. It translates VFS namespace mutations into append-only raw inode and dirent nodes, updating in-core dirent lists and link counts.

## Important APIs, Types, And Functions
Exported operation tables are `jffs2_dir_operations` and `jffs2_dir_inode_operations`. Static operation implementations include `jffs2_lookup()`, `jffs2_readdir()`, `jffs2_create()`, `jffs2_unlink()`, `jffs2_link()`, `jffs2_symlink()`, `jffs2_mkdir()`, `jffs2_rmdir()`, `jffs2_mknod()`, and `jffs2_rename()`.

## Control Flow
Lookup scans the directory's sorted `f->dents` list by name hash and returns the newest matching non-deletion dirent. Readdir emits dots, then live dirents while skipping deletion markers. Create-like operations allocate raw node structures, reserve flash space, call `jffs2_new_inode()`, write a metadata/data node as needed, initialize ACL/security, reserve/write a raw dirent, and insert the full dirent with `jffs2_add_fd_to_list()`. Unlink and rmdir write deletion dirents through `jffs2_do_unlink()`. Rename creates a new link then unlinks the old name.

## State And Persistence Behavior
Directory changes persist as new `JFFS2_NODETYPE_DIRENT` nodes and sometimes new raw inode metadata nodes. In-core state includes `jffs2_inode_info.dents`, `metadata`, `target`, `highest_version`, VFS inode link counts/times, and inode-cache `pino_nlink`. Older dirents are obsoleted rather than overwritten.

## Dependencies And Integration Points
This file depends on VFS dentry/inode APIs, ACL/xattr/security helpers, CRC32, `jffs2_do_create()`, `jffs2_do_link()`, `jffs2_do_unlink()`, `jffs2_write_dnode()`, `jffs2_write_dirent()`, and reservation logic from `nodelist.h`.

## Risks And Test Signals
Rename is explicitly non-atomic: if the new link succeeds and old unlink fails, the filesystem can expose an extra hard link and invalidates the target dentry. Error unwinding after partially written symlink/mkdir/mknod nodes is also important. Tests should cover ENOSPC at each reservation/write step, long names, hard-link restrictions, non-empty directory removal, rename-over-file/dir, crash recovery after partial namespace updates, and readdir ordering with deletion dirents.
