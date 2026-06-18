# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery.java

## Purpose
Tests block synchronization and lease recovery for contiguous HDFS files, including truncated metadata, failed recovery retry, append after recovery, ViewDFS integration, empty committed last blocks, aborted recovery, and committed blocks with content.

## APIs and Control Flow
`testBlockSynchronization` creates a replicated file, appends to hold a lease, expires the lease, checks generation stamps and sizes across replicas, and verifies safe mode blocks recovery. `testBlockRecoveryWithLessMetafile` truncates a block meta file, restarts a DN into recovery state, recovers the lease, and checks file length drops by one checksum chunk. `testBlockRecoveryRetryAfterFailedRecovery` finalizes one replica and deletes metadata to force retry. `testLeaseRecoveryAndAppend` and ViewDFS variant confirm another client cannot append until recovery succeeds, then can append. HDFS-14498 tests create committed-not-complete files with zero or one byte and verify manual and lease-manager recovery. `testAbortedRecovery` fakes an RBW report and completes without pipeline update, then expects the block to be dropped. `createCommittedNotCompleteFile` drives low-level Namenode create/addBlock/complete and optional aborted `DFSOutputStream` writes.

## State, Dependencies, Integration
State spans block generation stamps, metadata files, under-construction inode state, lease manager timers, safe mode, block manager internals, and client stream aborts. Dependencies include `NameNodeAdapter`, `LeaseManager`, `BlockManager`, `DataNodeTestUtils`, `TestInterDatanodeProtocol`, `DFSOutputStream`, `CryptoProtocolVersion`, and `ViewDistributedFileSystem`. It integrates low-level Namenode RPCs, DN dataset state, and public recover/append APIs.

## Risks and Test Signals
Signals include recovered file length, lease-holder disappearance, deleted block state, append/readback content, replica generation stamp equality, and safe-mode lease count. Risks are timing around lease expiry, direct block metadata corruption, low-level internal RPC usage, and environment-sensitive DN restart/recovery behavior.
