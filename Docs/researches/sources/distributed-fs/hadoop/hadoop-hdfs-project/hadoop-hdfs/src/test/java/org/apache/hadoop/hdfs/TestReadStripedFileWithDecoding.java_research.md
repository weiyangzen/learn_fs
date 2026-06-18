# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecoding.java

Purpose: tests striped EC client read and NameNode block-management behavior when internal EC blocks are corrupt, invalidated, or need parity/data decoding during reads.

Important APIs and types: `ReadStripedFileWithDecodingHelper`, `StripedFileTestUtil`, `LocatedStripedBlock`, `StripedBlockUtil.parseStripedBlockGroup`, `BlockManager`, `FSNamesystem`, `NameNodeAdapter`, `DatanodeDescriptor`, `DataNodeTestUtils`, `MiniDFSCluster.getBlockFile`, `cluster.corruptBlockOnDataNodes`, and `GenericTestUtils.waitFor`.

Control flow: setup creates a helper-initialized EC cluster for each test. `testReportBadBlock` writes a short file, locates the first internal data block file, overwrites it, disables heartbeats to keep the corrupt replica record visible, performs stateful read, and asserts corrupt replica count. `testInvalidateBlock` deletes a striped file while a DN heartbeat is disabled and checks the internal block reaches invalidate queues. `testCorruptionECBlockInvalidate` corrupts two data blocks, verifies both are reported corrupt after decoded read, selectively reenables heartbeats, and waits for each corrupt internal block to be invalidated. The remaining tests verify stateful reads with multiple corrupt blocks and a mixed data/parity corruption case.

State and persistence behavior: mutates actual MiniDFS block files and NameNode corrupt-replica/invalidate-block state. Heartbeats are deliberately disabled to freeze NameNode state for assertions and must be restored in `finally`. The tests exercise transient block reports, IBRs, corrupt replica maps, invalidation queues, and EC reconstruction interactions.

Dependencies and integration points: integrates filesystem writes, client striped reads, local DataNode storage files, NameNode `BlockManager`, corruption reporting RPCs, invalidation scheduling, and EC block group parsing. It depends on helper constants for cell size and unit counts.

Risks and edge cases: direct on-disk corruption can be storage-layout sensitive. Heartbeat disabling can leak if cleanup fails. The corruption/invalidation test encodes a specific race/regression around two corrupt data blocks and IBR ordering, so it is sensitive to asynchronous timing and uses waits. More-than-one-corrupted-block loops only up to less than parity count, keeping within decode tolerance.

Test signals: decoded reads must match expected bytes, corrupt replica map size reaches expected counts, invalidation queues contain the expected internal `Block`, and wait loops converge without timeout.
