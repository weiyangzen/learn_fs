# sources/distributed-fs/ceph-client/fs/squashfs/id.c

## Purpose

`id.c` maps compact uid/gid indexes stored in SquashFS inodes to 32-bit uid/gid values through the on-disk id lookup table.

## Important APIs, Types, and Functions

Public functions are `squashfs_get_id()` and `squashfs_read_id_index_table()`. It uses ID table macros from `squashfs_fs.h` and `msblk->id_table`.

## Control Flow

Mount code loads and validates the id index table. Inode creation calls `squashfs_get_id()` for uid and gid indexes; the function validates the index, reads the `__le32` disk id from compressed metadata, converts to CPU endian, and returns it.

## State and Persistence Behavior

`msblk->id_table` persists for the mount and points to metadata blocks containing actual id values. Inode uid/gid fields are populated in VFS inode state after lookup.

## Dependencies and Integration Points

`inode.c` depends on this for every inode. `super.c` loads and frees the id table. It uses `squashfs_read_table()` and `squashfs_read_metadata()`.

## Risks and Edge Cases

`no_ids == 0`, invalid id indexes, non-monotonic metadata pointers, or mismatched table size should fail mount or inode load. Bad id data can affect ownership visible to userspace.

## Test Signals

Images with many uid/gid values, boundary id indexes, malformed id tables, and stat output verification for file ownership.
