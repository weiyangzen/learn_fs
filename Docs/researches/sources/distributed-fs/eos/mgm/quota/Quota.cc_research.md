<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.cc -->
# sources/distributed-fs/eos/mgm/quota/Quota.cc

## Purpose
`Quota.cc` implements EOS MGM quota state, namespace quota-node binding, quota printing, admin set/remove operations, quota checks for writes and placement, statfs-style quota reporting, and quota accounting repair hooks. It bridges namespace quota statistics (`IQuotaNode`) with MGM global configuration and scheduler placement.

## Important APIs and functions
- Static state: `Quota::pMapQuota` maps normalized quota paths to `SpaceQuota*`, `pMapInodeQuota` maps quota container ids to `SpaceQuota*`, `pMapMutex` protects both, and `gProjectId` defaults to gid `99`.
- `SpaceQuota::SpaceQuota(path, cont_id)` binds to an existing container id, obtains or registers an `IQuotaNode`, and computes a layout size factor. It intentionally does not create a namespace container.
- `SpaceQuota::GetQuota`, `SetQuota`, `RmQuota`, `ResetQuota`, and `AddQuota` manipulate `mMapIdQuota`, using a packed `tag:id` index.
- `UpdateLogicalSizeFactor()` reads path attributes and policy layout to translate raw/logical bytes through `LayoutId::GetSizeFactor`.
- `UpdateFromQuotaNode()`, `AccountNsToSpace()`, `UpdateIsSums()`, and `UpdateTargetSums()` import live namespace accounting into the in-memory map and maintain aggregate "all user/group" values.
- `CheckWriteQuota()` enforces user, group, and project volume/inode limits for a requested write.
- `PrintOut()` emits table or monitoring output for user/group/summary quota views.
- `Quota::CreateQuotaDir()` is the only namespace-container creation path and refuses to create on non-`ENOENT` errors to avoid shadow quota directories.
- `Quota::CreateQuotaObj()` creates the in-memory `SpaceQuota` for an existing quota node and indexes it by path and quota-node id.
- `LoadNodes()` discovers quota-node ids from namespace quota stats, resolves URIs, creates missing in-memory objects by container id, and refreshes them.
- `SetQuotaTypeForId()` creates/binds the quota node if needed, sets logical and raw volume quota values, and persists config engine entries.
- `RmQuotaTypeForId()`, `RmQuotaForId()`, `RmQuotaForTag()`, and `RmSpaceQuota()` remove quota values or nodes from memory, config, and namespace quota registration.
- `GetResponsibleSpaceQuota()` finds the longest quota path prefix for a data path; `Exists`, `ExistsResponsible`, `GetResponsibleSpaceQuotaPath`, `QuotaByPath`, and `QuotaBySpace` wrap lookup variants.
- `FilePlacement()` checks physical space membership, space quota enablement, `CheckWriteQuota`, nominal physical quota, and then delegates placement to `Scheduler::FilePlacement`.
- `MapSizeCB()` computes physical usage as file size times layout size factor and is registered during QDB namespace boot.
- `RemoveFile()` and `AddFile()` update namespace quota accounting by file id, used by conversion and repair flows.
- `RefreshFromNsQuota()` drops cached "is" values for an exact quota path and refreshes from namespace accounting.

## Control flow
Quota setup flows from admin commands or master promotion. Admin `quota set` calls `SetQuotaTypeForId()`, which normalizes the path, ensures the backing container exists via `CreateQuotaDir()`, ensures a `SpaceQuota` object exists via `CreateQuotaObj()`, computes the relevant user/group and volume/inode tag, updates in-memory quota values, and writes corresponding config entries. Master promotion calls `Quota::LoadNodes()`, which discovers existing namespace quota nodes and creates in-memory objects without creating containers.

Write-time enforcement enters through `Quota::Check()` or `Quota::FilePlacement()`. Both locate the longest matching quota node and call `SpaceQuota::CheckWriteQuota()`. That method refreshes current namespace usage for the uid/gid and optional project quota, detects which targets are configured, and requires all configured user+group constraints to pass. If neither user nor group quotas are configured, project quota can authorize the write. Root uid bypasses quota checks.

Reporting flows through `Quota::PrintOut()`: it first reloads nodes, locks FsView and quota maps, then either prints all quota nodes or the responsible node for a supplied path. `SpaceQuota::PrintOut()` collects unique ids under its own mutex, optionally resolves uid/gid names outside the lock, and formats user, group, and aggregate tables.

## State and persistence
In-memory quota state lives in `SpaceQuota::mMapIdQuota`, keyed by packed quota tag and uid/gid/project id. `mDirtyTarget` tracks whether aggregate target sums need recomputation. `mQuotaNode` points at namespace-owned quota accounting, and `mLayoutSizeFactor` caches layout-dependent raw/logical translation.

Persistent namespace state includes quota-node registration on containers and live quota accounting in the namespace services. Persistent config state is stored through `gOFS->mConfigEngine` under the `"quota"` section. `CreateQuotaDir()` synchronizes the QuarkDB metadata flusher after creating a new quota directory so the directory is durable before quota registration/config persistence proceeds.

## Dependencies and integration points
This file depends on MGM globals (`gOFS`), namespace services (`IView`, `IContainerMD`, `IFileMD`, `IQuotaNode`, QuarkDB namespace group/flusher), `FsView`, `Scheduler`, `Policy`, `LayoutId`, mapping utilities, table formatting, and XRootD strings/mutexes. It is called by admin/user quota commands, WebDAV quota reporting, MGM open/file placement paths, recycle policy statistics, LRU logic, namespace repair commands, and conversion/tape-related flows that adjust quota accounting.

## Risks and edge cases
- Locking is complex: namespace locks, quota map locks, `SpaceQuota::mMutex`, and FsView locks appear in multiple combinations. Changes need strict lock-order review.
- `GetResponsibleSpaceQuota()` scans all quota paths linearly and uses prefix matching; path normalization and trailing slash behavior are critical to avoid accidental broader matches.
- `LoadNodes()` contains a suspicious `first` flag path where `first` is initialized true and only set false inside `if (!first)`, so intended re-grabbing behavior may not execute as written. The loop still releases locks inside the first iteration, making this worth closer review.
- `RmSpaceQuota()` wraps a raw pointer from `pMapQuota` in `std::unique_ptr` while also erasing from maps. That transfers deletion responsibility locally; callers must not retain stale `SpaceQuota*` after map removal.
- `SetQuotaTypeForId()` stores both logical and raw volume values. The `EOS_MGM_QUOTA_SET_BY_LOGICAL` environment variable changes interpretation of the input value, so admin tooling and tests must fix expected semantics.
- Several methods assume a fully initialized global `gOFS` and namespace services, making isolated unit tests difficult and failure modes process-global.
- Project quota behavior uses a magic gid (`99`) and overloads group quota tags. Incorrect configuration can cause double counting or unexpected project-only authorization.

## Test signals
No focused `Quota` unit test was found in the scanned output. Useful test coverage would include quota directory creation refusing non-`ENOENT`, logical/raw quota conversion with and without `EOS_MGM_QUOTA_SET_BY_LOGICAL`, longest-prefix responsible quota selection, project quota aggregation, root bypass, user+group both-required behavior, `QuotaByPath`/`QuotaBySpace` free-space semantics when no quota is set, and `RefreshFromNsQuota()` clearing only "is" tags. Integration signals already exist through admin quota commands, file placement in `XrdMgmOfsFile.cc` and `proc/user/File.cc`, recycle quota statistics, and conversion accounting calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.cc -->
