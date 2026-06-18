<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.hh -->
# sources/distributed-fs/eos/mgm/quota/Quota.hh

## Purpose
`Quota.hh` declares the MGM quota model. `SpaceQuota` represents one quota node and its in-memory counters/targets, while `Quota` provides static process-wide lookup, mutation, enforcement, reporting, placement, and accounting APIs.

## Important APIs and types
- `SpaceQuota` owns a display path, an `IQuotaNode*`, an `XrdSysMutex`, refresh timestamps, a layout size factor, dirty-target flag, and `mMapIdQuota`.
- `SpaceQuota::eQuotaTag` enumerates current, logical current, target, and aggregate quota counters for users and groups.
- `SpaceQuota::CheckWriteQuota()` is the key enforcement primitive for uid/gid plus requested bytes/inodes.
- `SpaceQuota::PrintOut()` formats a quota node for CLI/monitoring output.
- Private `SpaceQuota` helpers cover packed map indexing, quota get/set/reset/add/remove, namespace refresh, target/current sum recomputation, tag conversion, percentage/status rendering, enable checks, and quota-node pointer refresh.
- `Quota::IdT` distinguishes uid and gid quota operations; `Quota::Type` distinguishes volume, inode, and all operations.
- Public `Quota` APIs cover creating quota objects/directories, existence and responsible-node lookup, individual quota reporting, set/remove operations by id or tag, node removal, group statistics, namespace refresh, write checks, physical-size mapping, node loading/cleanup, printing, file placement, aggregate quota retrieval, quota lookup by path/inode, statfs data, add/remove file accounting, and forced namespace refresh.
- Static `Quota::pMapMutex` is public for cross-component locking, while maps are private.

## Control flow and state model
The header documents a deliberate split between container creation and quota-object creation. `CreateQuotaDir()` is the only API that may create a namespace directory and is reserved for explicit admin quota set operations. `CreateQuotaObj()` binds a `SpaceQuota` to an already existing namespace container id. This distinction prevents load/refresh paths from fabricating shadow quota directories after transient backend failures.

Most static APIs expect callers or implementations to normalize paths to trailing slash form. Responsible-node lookup is longest-prefix based, so quota enforcement can apply to subtrees without exact path matches. `FilePlacement()` is declared as scheduler-facing and requires the FsView lock. Several comments declare required lock ownership for refresh and quota-node address update paths.

## Persistence behavior
The header identifies two persistence layers: namespace quota nodes/containers and the config engine quota entries. `SpaceQuota` itself is an in-memory projection of namespace stats and configured targets. `pMapQuota` and `pMapInodeQuota` are rebuilt by `LoadNodes()` and destroyed by `CleanUp()`.

## Dependencies and integration points
The quota interface depends on scheduler placement types, common logging/layout/mapping/RWMutex utilities, namespace `IQuota`, XRootD strings, and Google dense hash headers. Integration points include MGM command processors for admin/user quota management, file placement/open code, WebDAV quota responses, recycle policy quota statistics, LRU/tape/conversion flows, and QDB namespace boot through `Quota::MapSizeCB` and `Quota::LoadNodes`.

## Risks and test signals
The API surface is mostly static and global, which simplifies call sites but makes dependency injection difficult. Public exposure of `pMapMutex` means external code can participate in locking, increasing lock-order risk. The comments around `CreateQuotaDir()` and constructor behavior are important invariants: tests should ensure non-admin load paths never create containers. Tag conversion helpers are private; behavior is validated indirectly through set/remove by id/tag and config entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.hh -->
