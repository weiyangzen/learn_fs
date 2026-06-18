# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerTestUtil.java

## Purpose

`DiskBalancerTestUtil` is a shared test helper for disk balancer suites. It creates randomized disk balancer model objects, synthetic clusters, imbalanced MiniDFSClusters, counts blocks per volume, and moves blocks between volumes to force planner and mover scenarios.

## Important APIs and types

- Model factories create `DiskBalancerVolume`, `DiskBalancerVolumeSet`, `DiskBalancerDataNode`, and `DiskBalancerCluster`.
- Constants `MB`, `GB`, and `TB` standardize model sizes.
- `NullConnector` feeds synthetic nodes into `DiskBalancerCluster`.
- `newImbalancedCluster` creates a real MiniDFSCluster with two disk volumes and moves all blocks to one destination volume.
- `getBlockCount` iterates `FsVolumeSpi.BlockIterator` for each block pool.
- `moveAllDataToDestVolume` calls `FsDatasetSpi.moveBlockAcrossVolumes` for every block on a source volume.

## Control flow

Random model helpers generate names, storage types, capacities, reserved bytes below 20 percent of capacity, and used bytes less than capacity minus reserved. Volume sets and data nodes are built by repeatedly adding random volumes by storage type. `createRandCluster` populates a `NullConnector`, calls `readClusterInfo`, and returns the resulting cluster model.

The MiniDFSCluster helper enables disk balancer, configures block and checksum sizes, writes a file, waits for replication, restarts DataNodes, obtains source and destination volumes for each DataNode, asserts source has blocks, moves all data from source to destination, asserts source is empty, restarts again, and returns the intentionally imbalanced cluster. Block counting can optionally assert each block pool has blocks.

## State and persistence behavior

Model helpers are in-memory and randomized from monotonic time. MiniDFSCluster helpers create actual block files and mutate their volume locations by moving blocks. Restart calls persist the resulting imbalance to DataNode storage.

## Dependencies and integration points

The helper bridges disk balancer model classes, connector abstractions, MiniDFSCluster, HDFS block creation, `FsDatasetSpi` volume movement, and `FsVolumeSpi` block iterators. Many disk balancer tests rely on it for reproducible imbalance setup.

## Risks and edge cases

- Random model data can make scale and serialization tests less deterministic.
- `newImbalancedCluster` requires exactly two storage capacities.
- Deprecated `new Double(temp).longValue()` style appears but only affects test utility implementation.
- Moving all blocks directly through the dataset bypasses planner validation and assumes volume references remain valid during iteration.

## Test signals

As a utility, its signals are indirect: generated models have valid capacities and usage, clusters can be serialized and planned, source volume block counts drop to zero after movement, destination volumes accumulate blocks, and restarted clusters preserve the forced imbalance.
