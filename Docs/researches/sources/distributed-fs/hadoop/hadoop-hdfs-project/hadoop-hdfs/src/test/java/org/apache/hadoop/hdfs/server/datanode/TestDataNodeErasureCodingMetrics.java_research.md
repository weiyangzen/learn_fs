# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeErasureCodingMetrics.java

## Purpose
This test validates DataNode erasure-coding reconstruction metrics for full and partial striped block groups.

## Important APIs, Types, and Functions
- Default EC policy from `StripedFileTestUtil` defines data units, parity units, cell size, and block group geometry.
- `doTest` writes a striped file, kills one DataNode participating in the last block group, forces reconstruction, and waits for completion.
- `getLongMetric` and `getLongMetricWithoutCheck` aggregate metrics across all DataNodes.
- Metrics under test include reconstruction tasks, failed tasks, decoding time, bytes read/written, remote bytes read, and read/decoding/write time millis.
- `setDataNodeDead` marks a DataNode dead in the NameNode block manager.

## Control Flow and Behavior
Setup starts `groupSize + 1` DataNodes, configures block size, enables the default EC policy, and sets it on root. Each test writes a file length chosen to represent full or partial block-group reconstruction. `doTest` generates data, writes the file, waits for block groups to be reported, identifies a DataNode from the last striped block, shuts it down, marks it dead, waits for computed reconstruction work, triggers heartbeats, calculates the expected total block count, and waits for all reconstruction to finish. Tests then assert metric values.

## State and Persistence
The tests create real striped files, block groups, dead DataNode state, and reconstructed blocks. Metrics are sampled from live DataNode metrics records and summed.

## Dependencies and Integration Points
The file integrates MiniDFSCluster, `DistributedFileSystem`, EC policy management, `LocatedStripedBlock`, BlockManager work computation, NameNode adapter access to `DatanodeDescriptor`, and Hadoop metrics assertions.

## Risks and Edge Cases
Covered risks include byte accounting for full group reconstruction, reconstructing a very small partial block, reconstructing a full block in a partial group, reconstructing a partial block in a partial group, and ensuring local reconstruction does not count remote bytes read in these scenarios. Timing depends on block manager work scheduling and heartbeats.

## Test Signals
Signals are zero initial timing counters, one successful reconstruction task, zero failed tasks, positive decoding and timing counters, exact bytes read/written expectations for each file geometry, zero remote bytes read, positive computed datanode work, and reconstruction completion.
