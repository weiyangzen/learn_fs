<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.cc -->
# sources/distributed-fs/eos/mgm/placement/ClusterMap.cc

Source read size: 240 lines, 7003 bytes.

## Purpose

Implements RCU-managed cluster snapshot publication and `StorageHandler`, the builder used to construct placement data from EOS filesystem views.

## Important APIs, Types, and Functions

Key methods are `ClusterMgr::getStorageHandler`, `getClusterData`, `addClusterData`, `setDiskStatus`, `setDiskWeight`, `getStorageHandlerWithData`, `getStateStr`, and `StorageHandler::{addBucket,addDisk,addDiskSequential,addGeoTag,getUniqueHash}`.

## Control Flow

`StorageHandler` accumulates buckets, disks, weights, and geotags in a local `ClusterData`. Its destructor publishes the completed snapshot through `ClusterMgr::addClusterData`, which swaps an atomic unique pointer under the RCU mutex and increments the epoch. Disk status updates acquire RCU read locks and mutate atomics in the current snapshot. Geotags are split on `::`, each segment is hashed with XXH3, and rare hash collisions are resolved by appending a nonce before rehashing.

## State and Persistence Behavior

All state is in memory. `ClusterMgr` owns the current snapshot pointer and epoch. `StorageHandler` publishes on destruction, making object lifetime part of the commit protocol.

## Dependencies and Integration Points

Depends on `ClusterDataTypes`, `RCULite`, `AtomicUniquePtr`, and xxhash. It is fed by `EosClusterMgrHandler` in `FsScheduler` and read by `FlatScheduler` and placement strategies.

## Risks and Edge Cases

Publishing in the `StorageHandler` destructor is convenient but risky if a partially built handler exits early. `addBucket` uses `parent_index != bucket_id`, comparing an index to an id, so root special-case logic is subtle. Nonsequential disk insertion resizes vectors and may leave default disk slots. `addGeoTag` currently omits the final segment after the last `::`.

## Test Signals

Test snapshot publication and epoch increments, RCU readers during swap, sequential and sparse disk insertion, bucket parent item lists and total weights, hash collision fallback, geotag parsing including single/no-delimiter tags, and diagnostic state strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.cc -->
