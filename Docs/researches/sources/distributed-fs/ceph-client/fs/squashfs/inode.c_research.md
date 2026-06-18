# sources/distributed-fs/ceph-client/fs/squashfs/inode.c

## Purpose

`inode.c` creates and initializes VFS inodes from packed SquashFS inode metadata. It decodes all regular, directory, symlink, device, FIFO, socket, and extended inode formats and attaches the correct VFS operations.

## Important APIs, Types, and Functions

Public functions/objects are `squashfs_iget()`, `squashfs_read_inode()`, and `squashfs_inode_ops`. Internal `squashfs_new_inode()` fills common inode fields. Important types are `union squashfs_inode`, on-disk inode structs, and `struct squashfs_inode_info`.

## Control Flow

`squashfs_iget()` uses `iget_locked()` and only reads metadata for new inodes. `squashfs_read_inode()` reads the base inode, validates mode/type setup, resets the metadata cursor, then switches on inode type. Each case reads the type-specific struct, fills VFS mode, size, nlink, operations, address-space operations, device numbers, fragment state, block-list location, directory index state, parent inode, and optional xattr id.

## State and Persistence Behavior

VFS inode fields persist in the inode cache. SquashFS-private inode state stores packed metadata locations and fragment/xattr/directory-index data. The filesystem is read-only; no inode writeback state is generated.

## Dependencies and Integration Points

It depends on id lookup, fragment lookup, xattr lookup, directory/file/symlink operation tables, special inode helpers, and metadata reading. `super.c` calls it for the root inode; directory lookup and export code call `squashfs_iget()`.

## Risks and Edge Cases

Malformed inode types, zero inode numbers, invalid uid/gid indexes, impossible fragments on block-aligned files, symlinks larger than a page, negative large-file sizes, or bad xattr ids must reject the inode. Mode type bits are expected unset in on-disk common mode before the switch sets them.

## Test Signals

Mount images containing every inode type, hard links, large regular files, sparse files, fragments, xattrs, special files, corrupt inode metadata, and repeated lookup/export paths that reuse cached inodes.
