# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_lookup.c

## Purpose
Implements the AFS lookup vnode operation plus mountpoint resolution, fakestat substitution, `@sys` expansion, dynroot lookup, and directory-neighbor bulk status prefetch. This file is the main name-to-vcache bridge for the cache manager.

## Important APIs, Types, and Functions
`afs_lookup` is the exported vnode lookup entry. `EvalMountData` parses mountpoint text, cell references, numeric volume IDs, vnode/unique suffixes, readonly/backup preferences, and linked-cell fallback. `EvalMountPoint` resolves mountpoint vcaches into target volume root FIDs. `afs_InitFakeStat`, `afs_EvalFakeStat`, `afs_TryEvalFakeStat`, and `afs_PutFakeStat` implement fakestat lifetime around mountpoint-to-root substitution. `afs_ENameOK`, `Check_AtSys`, `Next_AtSys`, and `afs_AtSys_SetType` implement `@sys` validation and iteration. `afs_DoBulkStat` and `afs_ShouldTryBulkStat` opportunistically create and populate vcaches using `RXAFS_InlineBulkStatus` or `RXAFS_BulkStatus`.

## Control Flow and State
`afs_lookup` creates a `vrequest`, enters the disconnected lock, optionally fakestats the parent, verifies parent status, handles `"."`, `".."`, dynroot mount directory names, static dynroot mount redirection, DNLC hits, and directory blob lookup via `afs_dir_LookupOffset`. Misses can retry for dynroot AFSDB discovery or readonly directory cache refresh. If the target is not already statted, lookup may call `afs_DoBulkStat` before falling back to `afs_GetVCache` or `afs_LookupVCache`. Mountpoint targets are evaluated when forced by fakestat settings or cached `CMValid` metadata. Successful lookups enter the DNLC unless the result is an unevaluated mountpoint or a direct cache hit.

The code updates vcache parent hints, `CMValid`, mountpoint target roots, volume `dotdot` and `mtpoint`, `last_looker`, callback state, and DNLC entries. Bulk stat temporarily stores a sequence number in `f.m.Length` while `CBulkFetching` is set, then merges status only if the sequence still matches. It also updates `CBulkStat`, `CTruth`, `CStatd`, `CRO`, `CBackup`, and `CForeign`.

## Dependencies and Integration Points
Depends on vcache/dcache locking, directory package calls, `afs_GetVolume*`, `afs_GetVCache`, callback queues, RX fileserver RPCs, `afs_Analyze`, DNLC APIs, dynroot APIs, NFS exporter `EXP_SYSNAME`, global sysname state, and platform-specific vnode finalization for Darwin.

## Risks and Test Signals
Bulk stat is race-sensitive and deliberately conservative; misuse of `f.m.Length` while `CBulkFetching` is set would corrupt file size semantics. Lookup suppresses internal `ENOENT` in many paths to avoid negative-cache poisoning. Mountpoint parsing temporarily edits strings in place. `@sys` expansion allocates large-space buffers and must free only when ownership changed. Lock ordering across vcache, dcache, callback hash, and global vcache locks is complex.

Test lookup of `.`, `..`, volume roots, mountpoints, dynroot cells, dynroot mount names, `cell:volume` numeric names, cross-cell mountpoints, backup/readonly volume preference, `@sys` names, DNLC hit/miss paths, bulk stat enabled/disabled/stressed/offline cases, readonly retry after stale directory data, and error translation through `afs_CheckCode`.
