# sources/distributed-fs/ceph-client/fs/squashfs/xattr_id.c

## Purpose

`xattr_id.c` maps xattr ids stored in extended inodes to xattr metadata locations, counts, and sizes, and loads the xattr id index table at mount.

## Important APIs, Types, and Functions

Public functions are `squashfs_xattr_lookup()` and `squashfs_read_xattr_id_table()`. It uses `struct squashfs_xattr_id` and `struct squashfs_xattr_id_table`.

## Control Flow

Mount reads the xattr id table header at `table_start`, extracts the xattr table start and id count, validates nonzero count and exact index table length to the end of the filesystem, reads the index table, and validates metadata-block pointer ordering plus xattr table ordering. Inode load calls `squashfs_xattr_lookup()` to read one id record and fill private inode xattr fields.

## State and Persistence Behavior

`msblk->xattr_id_table`, `msblk->xattr_table`, and `msblk->xattr_ids` persist for the mount. Per-inode xattr fields are derived from the id record.

## Dependencies and Integration Points

Used by `super.c` and `inode.c`; `xattr.c` later consumes the per-inode xattr location/count/size. It depends on `squashfs_read_table()` and `squashfs_read_metadata()`.

## Risks and Edge Cases

The table is located at the end of the filesystem, so length checks are tight. Bad index ordering or xattr table start can otherwise send xattr reads into unrelated metadata. `index >= xattr_ids` is rejected.

## Test Signals

Images with many xattr ids, out-of-line xattr values, corrupted xattr id table length/order, and xattr-disabled mount behavior through `xattr.h`.
