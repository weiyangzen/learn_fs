# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/DatanodeCacheManager.java

## Purpose

`DatanodeCacheManager` caches live DataNode storage reports for SPS block-movement planning. It refreshes reports at a configured interval, filters out storage volumes without remaining capacity, builds an SPS `DatanodeMap`, and caches the matching network topology.

## Important APIs, Types, And Functions

State includes `DatanodeMap datanodeMap`, `NetworkTopology cluster`, `refreshIntervalMs`, and `lastAccessedTime`. The main API is `getLiveDatanodeStorageReport(Context spsContext)`, with package-private `getCluster()` for the topology.

## Control Flow

Each call checks monotonic time since the last access. If the refresh interval elapsed, it resets the map, fetches live DataNode storage reports from context, walks each storage report, records only storage types and remaining sizes where remaining space is positive, adds the target DataNode to the map, and asks context for a topology built from that map. Calls before the interval expires return the existing map and cluster.

## State And Persistence Behavior

The cache is entirely in-memory and is not persisted. `lastAccessedTime` is updated on every call, so refresh cadence is based on access intervals. The returned `DatanodeMap` is the mutable cached object.

## Dependencies And Integration Points

It depends on SPS `Context`, `StoragePolicySatisfier.DatanodeMap`, `DatanodeStorageReport`, `StorageReport`, storage types, `NetworkTopology`, DFS configuration keys, and monotonic time. It feeds SPS target selection.

## Risks And Edge Cases

Updating `lastAccessedTime` before successful refresh means a failed refresh can delay the next attempt depending on caller behavior. There is no internal synchronization, so concurrent SPS callers could race on reset/add/topology updates. Storage with zero remaining capacity is excluded, which is appropriate for target selection but can hide otherwise live nodes. A zero refresh interval refreshes every call.

## Test Signals

Tests should verify refresh interval behavior, filtering of zero-capacity storage, topology refresh, cache reuse before interval expiry, IOException propagation from context, and behavior under empty live reports.
