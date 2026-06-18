# sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.h

## Purpose
Defines JFS block-map geometry, dmap/dmapctl/dbmap structures, conversion macros, buddy-tree helpers, and exported allocator APIs.

## Important APIs, types, and functions
Constants define dmap coverage, bitmap word sizes, tree sizes, control levels, max AGs, and max map size. Macros include `BLKTODMAP`, `BLKTOL0`, `BLKTOL1`, `BLKTOCTL`, `BLKTOAG`, `AGTOBLK`, `BLKSTOL2`, `NLSTOL2BSZ`, `LITOL2BSZ`, `BUDSIZE`, and `BLKTOCTLLEAF`. Structures include `dmaptree`, `dmap`, `dmapctl`, `dbmap_disk`, `dbmap`, and runtime `bmap`. Exports cover mount, allocation/free, persistent-map update, sync, bottom-up allocation, extend/finalize, map-size calculation, and AG discard.

## Control flow
`jfs_dmap.c` uses these definitions to locate dmap/control pages and update summary trees. Public callers operate on block ranges and `ipbmap`; the implementation uses the macros to translate aggregate blocks to map pages and AGs.

## State and persistence behavior
`dbmap_disk`, `dmap`, and `dmapctl` are on-disk little-endian state. `bmap` is in-memory state attached to the superblock with lock, active AG counters, and converted free counts. `wmap` tracks working allocation; `pmap` tracks persistent allocation.

## Dependencies and integration points
Depends on JFS transaction types and is consumed by inode, extent, free-space, discard, and resize code.

## Risks and test signals
Test conversion macros at boundaries, all AG sizes, max map sizes, endian conversion, layout stability, and allocation/free invariants after remount.
