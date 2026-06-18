# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestStoragePolicySatisfierWithStripedFile.java

## Purpose
`TestStoragePolicySatisfierWithStripedFile` is a slow integration suite for external Storage Policy Satisfier behavior on erasure-coded striped files. It verifies block movement from `DISK` to `ARCHIVE` for full stripes, partial target availability, low-redundancy restart scenarios, and no-target scenarios.

## Important APIs, Types, and Functions
The file uses `MiniDFSCluster` with multi-storage DataNodes, `StoragePolicySatisfier`, `ExternalSPSContext`, `NameNodeConnector`, `HdfsAdmin.satisfyStoragePolicy`, `ClientProtocol`, `ErasureCodingPolicy`, `StripedFileTestUtil`, `LocatedBlocks`, `LocatedBlock`, `StorageType`, and storage policy constants such as `HOT` and `COLD`. Helpers are `startSPS`, `initConfWithStripe`, `waitExpectedStorageType`, and `waitForAttemptedItems`.

## Control Flow
`init` configures external SPS mode, short DataNode cache refresh, high retry attempts, and a stripe block size based on default EC policy. The full-stripe test starts DataNodes with enough ARCHIVE targets, writes an EC file under a HOT policy, starts additional archive-only DataNodes, switches to COLD, calls `satisfyStoragePolicy`, and waits until all data/parity blocks report ARCHIVE storage. Partial-target tests use limited ARCHIVE availability, expect some attempted items to remain, and verify only reachable blocks move. The low-redundancy test stops all DataNodes, restarts the NameNode and only part of the DataNodes, starts movement, then restarts the rest and waits for full placement. The no-target test keeps only DISK storage and verifies SPS attempts but block storage remains DISK.

## State and Persistence Behavior
State includes NameNode storage policy xattrs, EC block groups, DataNode storage reports, SPS queues, attempted item monitor state, and cluster restart state in the low-redundancy case. It does not persist across full cluster shutdown beyond the test scenario restart.

## Dependencies and Integration Points
This is broad HDFS integration: EC file creation, block placement, DataNode storage types/capacities, heartbeats, external SPS service startup, NameNodeConnector mover identity, and HdfsAdmin/client protocol operations.

## Risks and Edge Cases
Risks include SPS choosing an invalid target for striped parity/data blocks, local movement not being preferred when an existing DataNode has the target storage type, low-redundancy files stalling movement until DataNodes return, no-target loops, and asynchronous heartbeat/cache timing flakiness. The tests use polling with timeouts and explicit heartbeat triggers.

## Test Signals
Signals include initial `LocatedBlocks` storage-type assertions, `StripedFileTestUtil.verifyLocatedStripedBlocks`, exact expected ARCHIVE/DISK counts, expected block-location counts, and attempted item count waits.
