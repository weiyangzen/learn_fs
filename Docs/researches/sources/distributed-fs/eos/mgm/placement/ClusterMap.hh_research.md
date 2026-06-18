<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.hh -->
# sources/distributed-fs/eos/mgm/placement/ClusterMap.hh

Source read size: 125 lines, 4228 bytes.

## Purpose

Declares the placement cluster snapshot manager and builder API.

## Important APIs, Types, and Functions

Defines `RCUMutexT`, `ClusterMgr`, nested `ClusterDataPtr`, and `StorageHandler`. Public operations include snapshot builders, RCU-protected snapshot access, live disk status/weight updates, state string generation, bucket/disk addition, and geotag helpers.

## Control Flow

`ClusterDataPtr` acquires an RCU read lock in its constructor and exposes pointer-like access to the snapshot until destruction. `StorageHandler` initializes a bucket vector, accumulates changes, and publishes by calling `ClusterMgr::addClusterData` from its destructor.

## State and Persistence Behavior

State is process-local and RCU-protected. The epoch counter tracks snapshot/weight changes for strategy caches and diagnostics; no disk persistence is performed here.

## Dependencies and Integration Points

Used by `FsScheduler`, `FlatScheduler`, and all placement strategies. Depends on common RCU primitives, atomic unique pointers, and the data types from `ClusterDataTypes.hh`.

## Risks and Edge Cases

The builder destructor has side effects, so copies/moves and early returns must be controlled. `ClusterDataPtr` assumes the raw pointer remains valid while its read lock is held. `setDiskWeight` increments epoch, but config/active status updates do not.

## Test Signals

Compile and unit coverage for snapshot lifetime, RCU lock scope, builder publication on destructor, mutable disk updates, and state string calls with empty and populated snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.hh -->
