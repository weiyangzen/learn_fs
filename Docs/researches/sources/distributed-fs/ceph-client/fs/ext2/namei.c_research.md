# sources/distributed-fs/ceph-client/fs/ext2/namei.c

Purpose: Implements ext2 VFS namespace operations: lookup, create, tmpfile, mknod, symlink, hard link, mkdir, unlink, rmdir, rename, parent lookup for exportfs, and directory/special inode operation tables.

Important APIs/types/functions: Exports `ext2_dir_inode_operations`, `ext2_special_inode_operations`, and `ext2_get_parent`. Static operations include `ext2_lookup`, `ext2_create`, `ext2_tmpfile`, `ext2_mknod`, `ext2_symlink`, `ext2_link`, `ext2_mkdir`, `ext2_unlink`, `ext2_rmdir`, `ext2_rename`, and helper `ext2_add_nondir`.

Control flow: Lookup validates name length, reads an inode number from `dir.c`, loads it with `ext2_iget`, and splices aliases. Create/mknod/symlink/mkdir allocate an inode, assign operation tables/data, mark it dirty, populate directory entries, and instantiate dentries. Symlinks choose fast in-inode storage when the target fits in `i_data`, otherwise use page-cache symlink storage. Unlink finds and deletes the directory entry, then decrements link count. Rename locates the old entry, optionally tracks `..` for moved directories, replaces or adds the new entry, updates ctimes/link counts, deletes the old entry, and fixes `..` when moving across parents.

State and persistence behavior: Namespace state persists through directory entries and inode link counts. Directory operations update parent/child ctime, mtime, size for directories, and link counts for hard links and directories. Tmpfile creates an inode not linked into a directory. Rename supports only `RENAME_NOREPLACE` among flags.

Dependencies and integration points: Relies on `ialloc.c` for new inodes, `dir.c` for directory entry editing, `inode.c` for inode loading and operation assignment, quota initialization, ACL/xattr operations, and exportfs parent reconstruction through `ext2_get_parent`.

Risks: Error paths must balance link counts and discard new inodes after partially completed creates/mkdirs/symlinks. Rename has multiple mapped folios and must release each exactly once. Directory moves must update both old and new parent link counts plus the child's `..` entry. Deleted inode references during lookup are treated as filesystem errors.

Test signals: create/link/unlink/mkdir/rmdir/rename xfstests; cross-directory rename of directories; replacement rename with non-empty target directory rejection; fast vs slow symlink thresholds; tmpfile open; exportfs parent lookup; long-name `-ENAMETOOLONG` handling.
