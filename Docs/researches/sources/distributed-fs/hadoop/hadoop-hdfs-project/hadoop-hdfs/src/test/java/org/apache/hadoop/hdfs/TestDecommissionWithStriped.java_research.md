# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithStriped.java

## Purpose
`TestDecommissionWithStriped` is the slow decommission suite for erasure-coded HDFS striped block groups. It verifies that datanode decommissioning preserves EC data availability, internal block indices, block tokens, checksum stability, and reconstruction correctness when some internal blocks are decommissioned, missing, duplicated, busy, or recovered from decommissioned storage.

## Important APIs, Types, and Functions
The fixture uses `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `FSNamesystem`, `BlockManager`, `BlockInfoStriped`, `LocatedStripedBlock`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `DataNodeProperties`, `StripedFileTestUtil`, and `DFSTestUtil`. Important helpers are `createConfiguration()`, `setup(@TempDir)`, `teardown()`, `testDecommission(int, int, int, String)`, `prepareBlockIndexAndTokenList(...)`, `assertBlockIndexAndTokenPosition(...)`, `getDecommissionDatanode(...)`, `writeStripedFile(...)`, `decommissionNode(...)`, `refreshNodes(...)`, `waitNodeState(...)`, `checkFile(...)`, and `getDatanodeOutOfTheBlock(...)`.

## Control Flow
Setup creates local include/exclude files, configures fast heartbeats/block reports/redundancy intervals, lowers EC reconstruction read buffer size, disables load consideration, starts a cluster with `dataBlocks + parityBlocks + 5` datanodes, enables the default EC policy, and marks a test directory as EC. Basic tests write striped files of different sizes, select datanodes that hold internal blocks, snapshot block-index and token associations, decommission one or two nodes via the exclude file and `refreshNodes`, then verify data with `StripedFileTestUtil.checkData`.

More targeted tests manipulate BlockManager internals. Busy-node tests increment pending reconstruction counters on a chosen `DatanodeDescriptor` to ensure the reconstruction scheduler avoids busy nodes while still reconstructing decommissioned internal blocks. Missing-block and failed-replication tests start decommissioning descriptors directly, manually queue EC block replication with `addECBlockToBeReplicated`, stop datanodes, wake pending reconstruction timers, and verify counts of live/decommissioning/decommissioned internal blocks. Recovery tests arrange duplicated internal blocks and decommissioned storage array positions to ensure reconstruction can use appropriate decommissioning sources without corrupting reads.

## State and Persistence Behavior
The class tracks EC policy parameters (`cellSize`, `dataBlocks`, `parityBlocks`, `blockSize`, `blockGroupSize`) as fixture state. Runtime state under test includes local host/exclude files, NameNode block group metadata, `BlockInfoStriped` storage/index arrays, block tokens, datanode admin states, pending replication counters, pending reconstruction queues, and live/dead datanode reports. Cleanup deletes the local decommission directory and shuts down the cluster. There is no disk persistence/restart scenario here; persistence focus is on in-memory EC metadata consistency during decommission operations.

## Dependencies and Integration Points
The suite integrates the EC read/write path (`StripedFileTestUtil`, `ErasureCodingPolicy`), NameNode block-management internals, datanode admin refreshes, token/index metadata in `LocatedStripedBlock`, DataNode lifecycle control, and JUnit ordering/timeouts. It also provides `createConfiguration()` as an extension point used by `TestDecommissionWithStripedBackoffMonitor` to run the same suite with the backoff monitor.

## Risks
These tests are sensitive to exact EC internal block ordering. `assertBlockIndexAndTokenPosition` guards against bugs where sorting locations moves `DatanodeInfo` entries without moving block indices or tokens. Busy-node tests depend on `replicationStreamsHardLimit` and manual pending counters; scheduler changes may require adjusted expectations. Several tests directly mutate descriptor admin state or storage arrays, so they are close to BlockManager internals and may fail after legitimate refactors unless the intended semantics are preserved.

## Test Signals
Passing tests indicate that decommissioned EC replicas are ordered after live replicas, duplicated internal blocks are counted correctly, all required data/parity block indices remain represented, file checksums remain stable, busy nodes are not selected for reconstruction, missing internal blocks can be rebuilt while nodes are decommissioning, and EC pread/read verification succeeds after complex decommission/recovery sequences.
