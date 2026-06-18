# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_extern.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_extern.h` declares cross-file interfaces used inside the FreeVxFS driver. The complete 49-line file was read for this report.

## Important APIs, Types, and Functions

Declarations include `vxfs_bmap1()`, `vxfs_read_fshead()`, `vxfs_immed_aops`, `vxfs_dumpi()` under diagnostic builds, `vxfs_blkiget()`, `vxfs_stiget()`, `vxfs_iget()`, `vxfs_evict_inode()`, `vxfs_dir_inode_ops`, `vxfs_dir_operations`, `vxfs_read_olt()`, `vxfs_aops`, `vxfs_get_page()`, `vxfs_put_page()`, and `vxfs_bread()`.

## Control Flow

The header has no execution. It defines the static driver layering: superblock mount code calls OLT and fileset-header readers, those read metadata inodes, inode code assigns directory and address-space operations, and subroutines call the block mapper.

## State and Persistence Behavior

No storage is owned by the header. It exposes functions that operate on superblock private state, inode private state, pagecache pages, and buffer heads.

## Dependencies and Integration Points

It provides a local integration surface between the eight FreeVxFS object files listed in the Makefile. The prototypes also encode which symbols are intentionally shared inside the driver rather than file-local.

## Risks and Edge Cases

Risk is signature drift: missing or stale prototypes can hide type mismatches or break builds when driver internals change. Since this is a C internal header, it also determines diagnostic-only availability of `vxfs_dumpi()`.

## Test Signals

Build coverage with `W=1`, sparse, and both diagnostic/non-diagnostic configurations is the main signal, plus link-time validation of the composite module.
