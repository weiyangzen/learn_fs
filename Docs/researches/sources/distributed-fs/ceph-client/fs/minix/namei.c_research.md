<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/namei.c -->
# sources/distributed-fs/ceph-client/fs/minix/namei.c

## Purpose
`fs/minix/namei.c` implements Minix directory inode operations: lookup, create, mknod, tmpfile, symlink, hard link, mkdir, unlink, rmdir, and rename. It bridges generic VFS directory requests to Minix directory-entry helpers and inode allocation/link-count rules.

## Important APIs, Types, and Functions
The exported table is `minix_dir_inode_operations`. `minix_lookup()` enforces `s_namelen`, resolves a directory entry through `minix_inode_by_name()`, and returns `d_splice_alias()`. `minix_mknod()`, `minix_create()`, and `minix_tmpfile()` allocate inodes with `minix_new_inode()` and initialize them through `minix_set_inode()`. `minix_symlink()` stores symlink text with `page_symlink()`. `add_nondir()` centralizes `minix_add_link()` plus `d_instantiate()` and cleanup on failure. Directory-specific operations use `minix_make_empty()`, `minix_empty_dir()`, `minix_find_entry()`, `minix_delete_entry()`, `minix_set_link()`, and `minix_dotdot()`.

## Control Flow
Creation allocates an inode, assigns file/special/symlink/dir operations, marks it dirty, inserts a directory entry, and instantiates the dentry. `mkdir` increments the parent link count, initializes the child with two links for `.` and parent reference, creates `.`/`..`, then links the new directory into the parent. On failure, it unwinds both child links and the parent link. `unlink` finds the directory entry, deletes it, releases the mapped folio, copies directory ctime to the victim, and decrements the victim link count. `rmdir` verifies parent link integrity and emptiness, calls unlink, then decrements parent and child directory links. `rename` locates old and optional new entries, handles directory `..`, replaces or adds the target entry, deletes the old entry, and updates link counts for cross-directory moves and overwritten directories.

## State and Persistence Behavior
Persistent changes are Minix directory entries, inode link counts, inode ctime, and page-cache-backed symlink data. Directory entry modifications happen through folio-mapped helper routines that dirty directory data elsewhere. Inode link count changes use VFS helpers such as `inode_inc_link_count()`, `inode_dec_link_count()`, and `drop_nlink()`, causing inode writeback through Minix inode update code. Renames of directories update the `..` entry to point at the new parent.

## Dependencies and Integration Points
This file depends on `minix.h` declarations and generic VFS namei locking/permission layers, which call these inode operations after parent locking and permission checks. It uses folio release helpers for directory-entry mappings and `page_symlink()` from core `fs/namei.c`. It deliberately passes `&nop_mnt_idmap` in `minix_create()` because Minix does not implement idmapped ownership handling in its create path.

## Risks
Link-count corruption is the main risk; the code explicitly checks zero nlink on unlink and low parent nlink on rmdir/rename and reports `-EFSCORRUPTED`. Rename has several delicate cases: replacing non-empty directories, moving directories across parents, updating `..`, and preserving balanced folio releases on every error path. Symlink length is limited to one filesystem block. `old_valid_dev()` rejects device numbers that cannot be represented by the legacy Minix special-file format.

## Test Signals
Test name length limits for 14/30/60-byte variants, create/link/unlink link-count transitions, mkdir/rmdir `.`/`..` correctness, rename over files and directories, cross-directory directory rename updating `..`, tmpfile creation, long symlink rejection, special-file device validation, and corruption tests for invalid link counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/namei.c -->
