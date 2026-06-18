
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManager.java

## Purpose
`TestBlockManager` is a broad integration and white-box test suite for HDFS block-management behavior. It covers rack-aware reconstruction, decommission and maintenance accounting, EC reconstruction source selection, safe-mode block-report processing, incremental block report queuing and batching, storage capacity and corruption handling, metasave output, placement policy satisfaction, invalidation semantics, datanode restart reports, and excess-redundancy timeout recovery.

## Important APIs, Types, and Functions
Core tested types include `BlockManager`, `DatanodeManager`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `BlockInfoContiguous`, `BlockInfoStriped`, `BlockReconstructionWork`, `NumberReplicas`, `LowRedundancyBlocks`, `InvalidateBlocks`, `BlockPlacementStatus`, and `CorruptReplicasMap`. The setup creates a mocked `FSNamesystem` with BM and global locks reported as held, an HA context that populates reconstruction queues, a real `BlockManager`, mocked `CacheManager`, six synthetic datanodes split across two racks, and helper methods such as `addNodes`, `removeNode`, `addBlockOnNodes`, `scheduleSingleReplication`, `fulfillPipeline`, `addBlockToBM`, `addUcBlockToBM`, and `addEcBlockToBM`.

## Control Flow and State
Early tests repeatedly schedule reconstruction for blocks placed on selected racks and assert source plus target rack selection under normal, partial decommission, full decommission, rack decommission, and single-rack cases. EC tests build striped block groups with duplicate internal blocks, busy datanodes, decommissioning sources, and missing blocks to validate source selection and skip decisions. Safe-mode block-report tests simulate first full reports, incremental-before-full reports, provided storage report counting, and under-construction blocks that should not enter needed reconstruction. MiniDFSCluster tests cover append pipeline updates, stale storage corrupt-replica deletion, remaining-capacity admission failure, queued block operations, async IBR metrics, failed/corrupt storage filtering in located blocks, EC placement satisfaction across changing rack counts, block report after datanode restart, NO_ACK invalidation, and timed-out excess replica deletion after datanode restart.

## State and Persistence Behavior
The class mutates `blocksMap`, `neededReconstruction`, `pendingReconstruction`, corrupt replica maps, excess redundancy maps, invalidate queues, datanode heartbeat state, and temporary NameNode/DataNode storage directories. It also writes temporary metasave files named `test.log` for output assertions and deletes them in finally blocks. Cluster tests persist real replicas in MiniDFSCluster directories, then remove, corrupt, or restart datanodes to verify NameNode state reconciliation.

## Dependencies and Integration Points
Dependencies span HDFS client APIs, MiniDFSCluster, EC policies, block reports, datanode fault injection, metrics, NameNodeAdapter, DataNodeTestUtils, `DFSOutputStream`, `DFSck`-adjacent block location paths, and Mockito spies. It is one of the main integration points between block placement, reconstruction scheduling, report processing, metrics, and administrative diagnostics.

## Risks and Test Signals
Risks are broad: probabilistic target selection, timeout-sensitive concurrency, stale mocks, leaked fault injectors, and filesystem cleanup around real cluster tests. High-value signals include exact pending reconstruction pipeline shape, queue length and metric assertions, located-block exclusion of failed/corrupt storage, metasave string contracts, EC placement status changes after rack expansion, deletion-report suppression for NO_ACK blocks, and excess-block retry after timeout.
