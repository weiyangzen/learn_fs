# sources/distributed-fs/ceph-client/fs/squashfs/export.c

## Purpose

`export.c` makes SquashFS exportable through exportfs/NFS-style file handles. It maps stable inode numbers from file handles to packed inode locations using the mount-time inode lookup table.

## Important APIs, Types, and Functions

The exported object is `squashfs_export_ops`; public table loader is `squashfs_read_inode_lookup_table()`. Internal functions are `squashfs_inode_lookup()`, `squashfs_export_iget()`, `squashfs_fh_to_dentry()`, `squashfs_fh_to_parent()`, and `squashfs_get_parent()`.

## Control Flow

At mount, `super.c` loads the inode lookup index and installs `s_export_op` when the image has an export table. During handle decode, exportfs passes inode numbers into `squashfs_export_iget()`, which reads the corresponding packed inode location and calls `squashfs_iget()`.

## State and Persistence Behavior

The lookup index persists in `msblk->inode_lookup_table`; actual inode-location entries remain compressed in metadata blocks and are read on demand. No writeback state exists.

## Dependencies and Integration Points

It integrates with VFS export operations, `generic_encode_ino32_fh`, `d_obtain_alias`, `squashfs_iget()`, and metadata reading. Parent lookup depends on `squashfs_inode_info.parent` filled by `inode.c`.

## Risks and Edge Cases

Invalid inode numbers, absent lookup table, corrupt table ordering, and bad parent inode fields can break export handles. Table validation checks size and monotonic metadata-block pointers.

## Test Signals

Mount exportable and non-exportable images, run exportfs/NFS handle round-trips, verify parent lookup for directories, and corrupt lookup index boundaries.
