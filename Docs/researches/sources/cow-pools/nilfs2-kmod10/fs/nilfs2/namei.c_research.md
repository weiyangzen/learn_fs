# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/namei.c

## Purpose

Implements NILFS2 pathname, directory inode, and export/NFS file-handle operations.

## Main Responsibilities

- Performs directory lookup and inode instantiation.
- Creates regular files, special files, symlinks, directories, hard links, unlinks, rmdirs, and renames inside NILFS transactions.
- Maintains link counts and dirty inode marking for directory mutations.
- Provides export operations to encode/decode file handles containing checkpoint number, inode number, generation, and optional parent identity.
- Defines inode operation tables for directories, symlinks, and special files.

## Important Functions

- `nilfs_lookup()` validates name length, resolves directory entries with `nilfs_inode_by_name()`, loads inodes with `nilfs_iget()`, and returns aliases through `d_splice_alias()`.
- `nilfs_create()` creates a new inode, assigns regular file ops and address-space ops, marks it dirty, and adds a directory entry.
- `nilfs_mknod()` creates special inode entries.
- `nilfs_symlink()` creates slow symlinks through `page_symlink()` and NILFS address-space ops.
- `nilfs_link()` increments link count, adds a new directory entry, and instantiates the dentry.
- `nilfs_mkdir()` increments parent link count, creates child directory, writes `.`/`..`, and links it.
- `nilfs_do_unlink()` finds the directory entry, validates inode number, deletes it, and decrements target link count.
- `nilfs_rename()` supports `RENAME_NOREPLACE`, replaces or adds target entries, updates `..` for moved directories, and fixes link counts.
- `nilfs_encode_fh()`, `nilfs_fh_to_dentry()`, and `nilfs_fh_to_parent()` implement export handle conversion.

## Dependencies and Interactions

- Uses directory helpers declared in `nilfs.h` and implemented elsewhere (`nilfs_find_entry`, `nilfs_add_link`, `nilfs_delete_entry`, `nilfs_set_link`, etc.).
- Uses `nilfs_new_inode()`, `nilfs_iget()`, `nilfs_mark_inode_dirty()`, `nilfs_setattr()`, `nilfs_permission()`, and `nilfs_fiemap()` from `inode.c`.
- Uses export structures from `export.h`.
- Uses root/checkpoint lookup for exported handles so snapshots can be represented by checkpoint number.

## Notable Behaviors and Edge Cases

- `nilfs_lookup()` maps `-ESTALE` for a deleted referenced inode into filesystem corruption via `nilfs_error()` and returns `-EIO`.
- All mutating namespace operations are transaction-wrapped and abort on error.
- Symlink length is limited to one filesystem block.
- `nilfs_do_unlink()` repairs zero link count to one before dropping it, warning about a nonexistent file deletion.
- Rename rejects all flags except `RENAME_NOREPLACE`.
- Export handle decode rejects reserved inode numbers except root and validates generation when provided.
