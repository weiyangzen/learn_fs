# sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.c

## Purpose
Implements the JFS aggregate block allocation map: mount/sync of the bmap descriptor, working-map allocation/free, persistent-map transaction updates, allocation group policy, filesystem extension, and trimming free AG ranges.

## Important APIs, types, and functions
Lifecycle: `dbMount()`, `dbUnmount()`, `dbSync()`, `dbFinalizeBmap()`, `dbMapFileSizeToMapSize()`. Allocation/free: `dbAlloc()`, `dbReAlloc()`, `dbFree()`, `dbAllocBottomUp()`, `dbExtendFS()`. Transaction map: `dbUpdatePMap()`. AG/trim: `dbNextAG()`, `dbDiscardAG()`. Core internals include `dbAllocAG()`, `dbAllocAny()`, `dbFindCtl()`, `dbAllocCtl()`, `dbAllocDmapLev()`, `dbAllocDmap()`, `dbFreeDmap()`, `dbAllocBits()`, `dbFreeBits()`, `dbAdjCtl()`, `dbSplit()`, `dbBackSplit()`, `dbJoin()`, `dbAdjTree()`, `dbFindLeaf()`, `check_dmapctl()`, and initialization helpers.

## Control flow
`dbMount()` reads and validates the on-disk descriptor, initializes counters/locks, and attaches the bmap. `dbAlloc()` uses hints in tiers: next to hint, near hint, same dmap, same AG, preferred AG, then anywhere. Small bottom-up updates hold read dmap locks; top-down control-tree searches hold write locks. `dbFree()` frees one dmap at a time and may issue online discard. `dbUpdatePMap()` updates persistent `pmap` bits and metapage logsync state. `dbDiscardAG()` temporarily allocates free extents, issues discard, then frees them.

## State and persistence behavior
Persistent state is `dbmap_disk`, dmap pages with `wmap`/`pmap`, and L0/L1/L2 dmapctl summary trees. Runtime `struct bmap` stores converted geometry, free counts, AG arrays, active AG counters, max free buddy, and the bmap mutex. `wmap` is working allocation; `pmap` is transaction-persistent state.

## Dependencies and integration points
Depends on metapage I/O, inode locks, superblock geometry, transaction/log manager, imap/extent users, discard helpers, memory allocation, and JFS error handling. File open/release updates `db_active[]`; extent code calls allocation/free APIs.

## Risks and test signals
High-risk areas are bitmap/tree consistency, AG free counts, lock ordering, endian conversion, multi-dmap backout leaks, dmapctl corruption validation, buddy split/join edge cases, persistent-map logsync ordering, resize geometry, and FITRIM temporary allocation. Test random allocate/free invariants, ENOSPC, multi-dmap extents, AG-boundary hints, concurrent writers, online discard/FITRIM, crash recovery, resize, corrupted control pages, I/O failures, and active AG preference.
