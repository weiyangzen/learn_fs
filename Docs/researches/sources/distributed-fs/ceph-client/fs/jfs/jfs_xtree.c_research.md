<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.c

## Purpose
`jfs_xtree.c` implements JFS extent allocation descriptor B+-trees. It maps logical file blocks to physical aggregate extents, inserts and extends extents, converts allocated-but-not-recorded ranges to recorded data, truncates file and metadata extents, initializes inline xtree roots, and exposes optional xtree statistics.

## Important APIs, types, and functions
The exported API is `xtLookup`, `xtInsert`, `xtExtend`, `xtUpdate`, `xtAppend`, `xtInitRoot`, `xtTruncate`, and `xtTruncate_pmap`. Internal structure centers on `xtpage_t`/`xtroot_t` pages from `jfs_xtree.h`, `xad_t` entries, `struct xtsplit` split descriptors, `struct btstack` search paths, metapages, and transaction locks. Core helpers are `xt_getpage`, `xtSearch`, `xtSplitUp`, `xtSplitPage`, and `xtSplitRoot`.

## Control flow
Lookups validate EOF unless bypassed, call `xtSearch`, then return the mapped physical address, flags, and contiguous length or the hole length up to the next extent. Search walks the root and internal pages by binary search, keeps a traversal stack, uses sequential access hints from `JFS_IP(ip)->btindex/btorder`, and pins the leaf containing the hit or insertion point. Inserts allocate data blocks when needed, mark new entries with `XAD_NEW`, and either shift a leaf or split leaf/internal/root pages upward. Append mode allocates bottom-up from a caller-specified contiguous region so bmap growth can consume the new area in order. `xtExtend` grows the preceding contiguous extent and inserts a continuation when `MAXXLEN` would be exceeded. `xtUpdate` replaces a subrange of a not-recorded extent, coalesces with neighboring recorded extents when logically and physically contiguous, and performs two- or three-way splits if the recorded range sits inside an existing extent.

Truncation is a backward bottom-up tree walk. `xtTruncate` frees or logs data and index extents depending on `COMMIT_PWMAP` versus `COMMIT_WMAP`, updates `nextindex`, collapses empty roots back to leaves, invalidates directory metapages on full directory truncation, and caps a transaction at `MAX_TRUNCATE_LEAVES` to avoid tlock/metapage deadlock. `xtTruncate_pmap` handles deleted-but-open files by freeing persistent-map resources in bounded transactions while leaving working-map access possible until final close.

## State and persistence behavior
Persistent state is the on-disk xtree encoded in inode inline roots and metapage index blocks. Entries store flags, logical offsets, physical addresses, and lengths. Runtime state includes pinned metapages, transaction locks (`tlckXTREE`, `tlckGROW`, `tlckNEW`, `tlckFREE`, `tlckTRUNCATE`), quota reservations, B+-tree search hints, and optional statistics. The code coordinates persistent map (`PMAP`) and working map (`WMAP`) semantics so unlink, truncate, and delayed close can commit in stages.

## Dependencies and integration points
It depends on JFS btree macros, metapages, block allocator `dbAlloc/dbFree/dbAllocBottomUp`, quota accounting, transaction manager `txLock/txFreeMap`, inode flags such as `COMMIT_Nolink`, and directory metadata invalidation helpers. Callers include file block mapping, symlink creation, bmap resize growth, unlink/rename zero-link cleanup, and generic truncate paths.

## Risks and test signals
High-risk areas are corrupt-page validation, split propagation while pins are transferred, quota rollback on split allocation failure, coalescing rules in `xtUpdate`, `MAXXLEN` overflow boundaries, root expansion/shrink interaction with inline EA space, and partial truncation requiring repeated transactions. Useful tests include sparse lookup holes, sequential and random extent insertion, root and internal splits, append-only bmap growth, conversion of not-recorded extents at left/middle/right positions, huge fragmented truncation, deleted-open-file cleanup, and fault injection for metapage/block allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.c -->
