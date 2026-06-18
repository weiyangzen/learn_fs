<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.cc -->
# sources/distributed-fs/eos/mgm/placement/FsScheduler.cc

Source read size: 351 lines, 11385 bytes.

## Purpose

Implements `FSScheduler`, the EOS-facing placement scheduler that rebuilds cluster data from `FsView`, exposes scheduling/access operations by space, and applies default or per-space strategy configuration.

## Important APIs, Types, and Functions

Key methods are `EosClusterMgrHandler::make_cluster_mgr`, `FSScheduler::updateClusterData`, `schedule`, `access`, `setDiskStatus`, `setDiskWeight`, `setPlacementStrategy`, `getPlacementStrategy`, `getStateStr`, and `isRunning`.

## Control Flow

The cluster handler reads `FsView::gFsView.mSpaceGroupView` under the view mutex, creates one `ClusterMgr` per space, adds a root bucket, adds group buckets from group indexes, and inserts each filesystem as a disk with config status, active status adjusted for boot state, capacity-derived weight, percent used, and geotag. `updateClusterData` publishes the new space map with an RCU write and marks the scheduler running. `schedule` resolves invalid strategy to the space/default strategy, reads the cluster map under RCU, gets the space snapshot, and retries placement up to ten times. `access` delegates read selection. Disk status/weight setters mutate the live cluster manager for a space. Per-space strategy updates copy and republish the strategy map under RCU.

## State and Persistence Behavior

The scheduler owns an RCU-protected map of spaces to cluster managers, an atomic default strategy, an optional RCU-protected per-space strategy map, and a running flag. Cluster state is rebuilt from `FsView`; it is not persisted here.

## Dependencies and Integration Points

Integrates placement with `FsView` space/group/filesystem views, `FlatScheduler`, `ClusterMgr`, filesystem status/config/geometry attributes, common RCU helpers, and EOS logging.

## Risks and Edge Cases

`make_cluster_mgr(const std::string&)` adds group buckets without passing parent id, relying on default parent `0`; root handling must be valid. Capacity-to-uint8 weight can truncate very large capacities. `schedule` retries without changing args, so repeated failure may not improve unless strategy state advances. `get_cluster_mgr` requires initialized `cluster_mgr_map`.

## Test Signals

Use fake `ClusterMgrHandler`/`FsView` data to test cluster rebuilds, multiple spaces, empty spaces, status and boot mapping, capacity weights, geotags, strategy fallback and per-space overrides, scheduling before initialization, and RCU map replacement under readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.cc -->
