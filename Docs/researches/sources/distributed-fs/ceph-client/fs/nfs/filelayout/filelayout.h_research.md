# sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.h

## Purpose
`filelayout.h` defines the data structures, constants, inline accessors, and cross-file prototypes for the pNFS NFSv4.1 files layout driver.

## Important APIs, types, and functions
It sets `NFS4_PNFS_MAX_STRIPE_CNT` to 4096 and `NFS4_PNFS_MAX_MULTI_CNT` to 256, reflecting a memory-saving representation of wire stripe indices as `u8`. `enum stripetype4` defines `STRIPE_SPARSE` and `STRIPE_DENSE`.

`struct nfs4_file_layout_dsaddr` represents decoded GETDEVICEINFO data: generic deviceid node, stripe count, compact stripe-index array, data-server count, and a flexible array of `struct nfs4_pnfs_ds *`. `struct nfs4_filelayout_segment` wraps a generic layout segment with striping mode, commit policy, stripe unit, first stripe index, pattern offset, deviceid, bound dsaddr, and file-handle array. `struct nfs4_filelayout` wraps a generic layout header with pNFS DS commit info.

Inline helpers include `FILELAYOUT_FROM_HDR`, `FILELAYOUT_LSEG`, `FILELAYOUT_DEVID_NODE`, and `filelayout_test_devid_invalid`. Prototypes expose data-server file-handle selection, stripe math, DS preparation, deviceid allocation/put/free, and unavailable-device tests.

## Control flow
The header is included by `filelayout.c` and `filelayoutdev.c`. `filelayout.c` owns layout segment decode, I/O, commits, and registration; `filelayoutdev.c` owns deviceid decode and DS connection. The shared structures let both files consistently translate layout segments into deviceid and data-server choices.

## State and persistence behavior
The structures describe cached runtime copies of MDS-provided layouts and deviceid information. References to deviceids and data servers are managed by pNFS caches, with RCU freeing on deviceid destruction. There is no local persistent state.

## Dependencies and integration points
The header depends on `../pnfs.h` and NFS/pNFS types. It is part of the module-private contract between layout routing code and deviceid management, and it exposes only the symbols needed across the two source files.

## Risks
The compact `u8` stripe-index representation requires strict validation that decoded stripe indices fit below 256 and below the DS count. Accessors assume `fl->dsaddr` is non-NULL when deriving the deviceid node, so callers must run deviceid validation first. Counted flexible arrays and file-handle arrays must be allocated and freed consistently.

## Test signals
Build tests should catch prototype drift. Runtime tests should cover maximum stripe counts, maximum multipath counts, invalid stripe indices, dense/sparse file-handle count validation, NULL dsaddr avoidance, and deviceid unavailable/invalid flags.
