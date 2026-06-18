<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.cc -->
# sources/distributed-fs/eos/mgm/scheduler/Scheduler.cc

## Purpose
Implements the MGM file placement and access scheduler facade. It tries the newer `mgm/placement/FsScheduler` flat scheduler first and falls back to the legacy `GeoTreeEngine` when a space is configured for geotree placement or when flat access/placement cannot satisfy the request.

## Important APIs and Functions
- Static state:
  - `Scheduler::pMapMutex`: protects `schedulingGroup`.
  - `Scheduler::schedulingGroup`: maps group tags or `uid:gid` strings to the next `FsGroup*` to try for rotating geotree placement.
- `Scheduler::getRequiredReplicas(unsigned long lid)`: returns `LayoutId::GetStripeNumber(lid) + 1` as `uint8_t`.
- `Scheduler::FlatSchedulerFilePlacement(PlacementArguments*)`: builds `placement::PlacementArguments`, honors explicit scheduling strategy override unless it is `kGeoScheduler`, calls `gOFS->mFsScheduler->schedule`, and copies selected fsids.
- `Scheduler::FilePlacement(PlacementArguments*)`: primary placement API; fast path through flat scheduler, fallback through `gOFS->mGeoTreeEngine->placeNewReplicasOneGroup`.
- `toGeoTreeSchedtype(...)`: local helper mapping scheduler type plus read/write mode to `GeoTreeEngine::SchedType`.
- `Scheduler::FlatSchedulerFileAccess(AccessArguments*)`: delegates access choice to `gOFS->mFsScheduler->access` unless the space strategy is geotree.
- `Scheduler::FileAccess(AccessArguments*)`: primary file access API; validates stripe availability and forced fsid, tries flat access, falls back to `GeoTreeEngine::accessHeadReplicaMultipleGroup`, then enforces `exclude_filesystems`.
- `Scheduler::ReshuffleFs(std::vector<unsigned int>&)`: rotates selected fsids by placing either min or max first based on parity of the fsid sum.

## Control Flow
Placement starts by calling `FlatSchedulerFilePlacement`; success returns immediately. If flat scheduling reports failure or a geotree strategy, the legacy path calculates `ncollocatedfs` from placement policy and layout type, derives an index tag from group tag or uid/gid, selects a scheduling group, and loops over groups. Groups already hosting replicas are tried first when geotree can resolve them from `alreadyused_filesystems`. Forced group selection fails immediately if the requested group cannot place all replicas. Non-forced placement rotates through `FsView::gFsView.mSpaceGroupView[spacename]`, updating `schedulingGroup` under `pMapMutex`.

Access starts with required stripe checks: RW needs `GetOnlineStripeNumber(lid)`, RO needs `GetMinOnlineReplica(lid)`. A forced fsid must already be one of the file locations. Flat access is attempted first. If it fails, geotree access marks locations tried via CGI as unavailable, then calls `accessHeadReplicaMultipleGroup`. After a successful scheduling decision, the method checks `exclude_filesystems` and, if needed, picks the first location not excluded and not unavailable; if none exists it returns `ENODATA`.

## State and Persistence
The only durable-in-process scheduler state here is `schedulingGroup`, used for group rotation fairness across placement calls. It is not persisted and is lost on MGM restart. All selected filesystem output is written through caller-provided vectors in `PlacementArguments` and `AccessArguments`.

## Dependencies and Integration Points
Depends heavily on global MGM state:
- `gOFS->mFsScheduler` for flat placement/access.
- `gOFS->mGeoTreeEngine` for geolocation-aware fallback.
- `FsView::gFsView.mSpaceGroupView` and `ViewMutex`; comments require callers to hold a read lock.
- `LayoutId` for stripe/layout decoding.
- `Quota::FilePlacement` delegates to `Scheduler::FilePlacement`.
Callers include file open/create paths in `mgm/ofs/XrdMgmOfsFile.cc`, user `File`/`Fileinfo` commands, and quota placement logic.

## Risks
- `FilePlacement` calls `FlatSchedulerFilePlacement` before validating `args`; callers rely on `PlacementArguments::isValid()`, but this function does not enforce it.
- `FlatSchedulerFilePlacement` assigns `ret.ids.begin() + n_replicas` without checking `ret.ids.size() >= n_replicas`; this depends on `mFsScheduler->schedule` contract.
- In the non-forced geotree path, `schedulingGroup[indextag]` is dereferenced through `find`; stale `FsGroup*` values could be hazardous if group objects are removed concurrently or not present in the current space.
- The required external `FsView::ViewMutex` locking is a sharp API contract; misuse can race with `mSpaceGroupView` and node state.
- `ReshuffleFs` accumulates fsids into an `int`, which can overflow for large vectors/high fsids, though only parity matters.
- `FlatSchedulerFileAccess` constructs `std::string spaceName(args->forcedspace)` without null checks; callers must set `forcedspace` before selecting flat access.

## Test Signals
The lower-level placement subsystem has broad coverage in `unit_tests/mgm/placement/SchedulerTests.cc` and `FsSchedulerTests.cc`, including flat scheduler strategies, excluded fsids, forced groups, weighted strategies, and concurrency. `test/microbenchmarks/mgm/BM_FlatScheduler.cc` benchmarks flat strategies. Direct tests for this facade’s geotree fallback, `FileAccess` post-filtering, and stale `schedulingGroup` rotation are less obvious.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.cc -->
