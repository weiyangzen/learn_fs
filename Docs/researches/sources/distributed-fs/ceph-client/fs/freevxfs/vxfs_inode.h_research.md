# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.h` defines FreeVxFS on-disk inode layouts, extent organization records, and the in-core inode private structure. The complete 169-line file was read for this report.

## Important APIs, Types, and Functions

Key definitions include `VXFS_ISIZE`, `VXFS_NDADDR`, `VXFS_NIADDR`, `VXFS_NIMMED`, `VXFS_NTYPED`, typed extent masks, `VXFS_TYPED_PER_BLOCK()`, typed extent type constants, `struct vxfs_immed`, `struct vxfs_ext4`, `struct vxfs_typed`, `struct vxfs_typed_dev4`, `struct vxfs_dinode`, `struct vxfs_inode_info`, field alias macros, and `VXFS_INO()`.

## Control Flow

The header has no independent flow. Its union layouts determine how `vxfs_inode.c` copies inode data and how `vxfs_bmap.c` maps extents.

## State and Persistence Behavior

`struct vxfs_dinode` is persistent on-disk state, including mode, ownership, size, timestamps, organization type, allocation metadata, generation, and organization-specific payload. `struct vxfs_inode_info` embeds the Linux `struct inode` and stores converted VxFS private fields for runtime use.

## Dependencies and Integration Points

It is included by most FreeVxFS source files and bridges VxFS disk structures to VFS inode instances through `VXFS_INO()`.

## Risks and Edge Cases

On-disk layout drift is the main risk. The organization union is copied raw, so all consumers must endian-convert fields at use time. The `vdi_fixextsize` alias appears to reference `regular` while the union member is named `i_regular`, which is a latent macro issue if used.

## Test Signals

Sparse endian checks, compile coverage for all macros, fixtures for each organization type, and fuzzing of typed extents and immediate payload sizes are useful.
