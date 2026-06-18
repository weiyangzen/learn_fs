# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetBlocks.java

## Purpose
Slow integration tests for block-location and balancer-oriented `NamenodeProtocol.getBlocks` behavior, including stale nodes, min block size, safe mode rejection, hot-block ordering, stale storage exclusion, and storage-type filtering.

## APIs and Control Flow
`testReadSelectNonStaleDatanode` writes an unclosed file, marks selected DNs stale by disabling heartbeats and manipulating last-update timestamps, then checks stale replicas move to the end of read locations. `testGetBlocks` creates a 13-block file, calls `getBlocks` with different sizes and min-block sizes, validates storage IDs, invalid arguments, nonexistent DN errors, `testBlockIterator`, and safe-mode failure. `testBlockKey` checks block hash/equality using grandfather generation stamps. `testGetBlocksWithHotBlockTimeInterval` verifies older file blocks are preferred before new ones. `testReadSkipStaleStorage` marks individual storage stale and all storages stale. `testChooseSpecifyStorageType` creates SSD and DISK files through storage policies and filters `getBlocks` by `StorageType`.

## State, Dependencies, Integration
State spans block maps, DN descriptors, storage infos, safe mode, heartbeat freshness, storage policies, and block locations. Dependencies include `MiniDFSCluster`, `DFSClient`, `NamenodeProtocol`, `BlockManagerTestUtil`, `DataNodeTestUtils`, `DFSTestUtil`, and `NameNodeProxies`. It directly integrates client reads, block-manager internals, balancer RPCs, and storage policy placement.

## Risks and Test Signals
Signals are exact block counts, exception classes/messages, ordering assertions, storage IDs/types, and iterator immutability checks. Risks are timing-sensitive stale-node simulation, safe-mode state cleanup, random block-key seed reproducibility only via stdout, and dependence on internal block/storage iteration order.
