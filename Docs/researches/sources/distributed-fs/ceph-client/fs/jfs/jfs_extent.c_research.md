# sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.c

Purpose: implements allocation, hinting, and record-state updates for regular-file extents in the JFS xtree.

Important APIs and functions: exported functions are `extAlloc`, `extHint`, and `extRecord`. Internal helpers are `extBalloc` and `extRoundDown`.

Control flow: `extAlloc` rejects read-only filesystems, starts an anonymous transaction, serializes with `commit_mutex`, clamps the request to `MAXXLEN`, computes file block offset from page number, optionally uses the previous extent as a contiguous allocation/extend hint, calls `extBalloc`, charges quota, and records the allocation through `xtExtend` or `xtInsert`. On any xtree failure it frees both blocks and quota. `extHint` looks up the previous page-sized extent and returns an XAD hint only when it maps exactly one page. `extRecord` converts an allocated-not-recorded extent to recorded by calling `xtUpdate` under the commit mutex.

State and persistence behavior: persistent state is xtree XAD entries plus block allocation map and quota accounting. `extAlloc` may insert XADs with `XAD_NOTRECORDED` for delayed record semantics. It marks the inode dirty and commits immediately if `COMMIT_Synclist` was set by anonymous page tlocks. `extBalloc` also updates the inode's active allocation group for regular files in the fileset, maintaining `bmap->db_active` counters to guide later inode allocation away from actively growing AGs.

Dependencies and integration: depends on `jfs_incore`, `jfs_inode`, `jfs_superblock`, `jfs_dmap`, `jfs_extent.h`, xtree operations (`xtLookup`, `xtInsert`, `xtExtend`, `xtUpdate`), quota APIs, anonymous transaction startup, and JFS block-map allocation (`dbAlloc`, `dbFree`). It integrates with writepage/get-block paths that need real disk extents.

Risks and edge cases: allocation degrades by powers of two down to one page, so callers must tolerate shorter-than-requested extents. Hint extension is valid only when extent offset, length, physical address, and not-recorded state line up. Quota failure and xtree failure must roll back block allocation. `extHint` treats a non-page-sized previous extent as corruption and returns `-EIO`.

Test signals: writes that allocate from no hint, contiguous extension of a previous extent, fallback to smaller extents under fragmentation, quota denial, `abnr` allocation followed by `extRecord`, active AG counter changes, and corrupt xtree hint detection.
