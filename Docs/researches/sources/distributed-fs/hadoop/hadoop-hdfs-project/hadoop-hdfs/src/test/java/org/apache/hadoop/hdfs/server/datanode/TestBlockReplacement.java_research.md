# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockReplacement.java

## Purpose
`TestBlockReplacement` validates DataNode block replacement and movement behavior, including throttling, invalid replacement cases, pinned blocks, same-node storage-type movement, and HA failover interaction with deletion reports.

## Important APIs, Types, and Functions
- `DataTransferThrottler#throttle` is tested directly.
- `DFSTestUtil.replaceBlock` drives data transfer replacement operations and expected `DataTransferProtos.Status` outcomes.
- `checkBlocks` polls NameNode block locations until expected replicas and locations are observed.
- `MiniDFSCluster`, `DFSClient`, `LocatedBlock`, `DatanodeInfo`, `ExtendedBlock`, and `StorageType` provide cluster and block metadata.
- `InternalDataNodeTestUtils.mockDatanodeBlkPinning` simulates pinned blocks.

## Control Flow and Behavior
The throttler test sends 6 MiB through a 1 MiB/s throttler and checks average throughput. The main replacement test creates a one-block file replicated to three racks, starts a fourth DataNode, identifies source, proxy, and destination nodes, then tests bad proxy, destination-already-has-block, valid replacement, and invalid delete-hint cases. Pinned-block coverage mocks all DataNodes as pinning the block and expects replacement to fail with `ERROR_BLOCK_PINNED`. Same-node movement uses a DataNode with DISK and ARCHIVE storage and replaces a block from DISK to ARCHIVE using the same node as source, proxy, and destination.

The HA test starts a two-NameNode HA cluster, makes NN0 active, writes a block, replaces it to a second DataNode, waits for deletion reporting, fails over to NN1, and asserts the block still has one valid location rather than a standby-generated stale delete.

## State and Persistence
All substantive tests use real MiniDFSCluster block files, storage types, block reports, deletion reports, and NameNode block maps. The replacement operation changes actual replica placement or storage type.

## Dependencies and Integration Points
The test integrates data transfer replacement protocol, rack-aware placement, storage policies/types, pinned block checks, NameNode over-replication deletion, block reports, HA edit tailing, DataNode descriptors through `NameNodeAdapter`, and DFS client block-location APIs.

## Risks and Edge Cases
Covered risks include accepting an invalid proxy source, copying to a destination that already has the block, incorrect delete-hint handling after over-replication, moving pinned blocks, same-node cross-storage transfer, and standby NameNode queuing an invalid delete while an add-block edit is not yet applied.

## Test Signals
Signals include boolean replacement outcomes, expected data-transfer status codes, polled block locations matching target replication and inclusion expectations, storage type changing to ARCHIVE for same-node movement, and stable single replica after HA failover.
