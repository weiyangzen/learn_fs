# sources/distributed-fs/ceph-client/fs/gfs2/rgrp.h

## Purpose
`rgrp.h` declares the GFS2 resource-group allocator interface used by inode, bmap, xattr, superblock, recovery, and debug code. It also defines reservation sizing constants and the small helper type for multi-rgrp lock acquisition.

## Important APIs, Types, And Functions
`RGRP_RSRV_MINBLKS` and `RGRP_RSRV_ADDBLKS` tune minimum and growth sizes for multi-block reservations. The header exports rgrp lookup and lifecycle helpers (`gfs2_blk2rgrpd`, `gfs2_rgrpd_get_first`, `gfs2_rgrpd_get_next`, `gfs2_clear_rgrpd`, `gfs2_rindex_update`, `gfs2_rgrp_go_instantiate`, `gfs2_rgrp_brelse`) and allocator APIs (`gfs2_inplace_reserve`, `gfs2_inplace_release`, `gfs2_alloc_blocks`, `gfs2_free_meta`, `__gfs2_free_blocks`, `gfs2_free_di`, `gfs2_unlink_di`).

`struct gfs2_rgrp_list` packages an array of `gfs2_rgrpd *` and matching glock holders so callers can collect all rgrps touched by a multi-block operation, allocate holders, lock them together, then free the list.

## Control Flow And State
Callers typically refresh the rindex, locate rgrps, reserve space, begin a transaction, allocate or free, and release the reservation. The inline `gfs2_rs_active` tests whether an inode reservation is linked into a resource-group reservation tree. `rgrp_contains_block` provides the basic address-range predicate used throughout allocation and validation.

## Dependencies And Integration Points
The declarations depend on GFS2 in-core structures and Linux slab/uaccess headers. This header is consumed by file/block mapping, inode creation/deletion, xattr storage, superblock statfs, and debug dump code.

## Risks And Test Signals
Because this header exposes low-level allocation primitives, misuse risks include allocating without an active reservation, freeing outside a single rgrp, or assuming a reservation is active without checking its rbtree node. Compile coverage should catch signature drift; runtime signals come from rgrp consistency checks, tracepoint output, and stress tests around ENOSPC, unlink, and xattr block allocation.
