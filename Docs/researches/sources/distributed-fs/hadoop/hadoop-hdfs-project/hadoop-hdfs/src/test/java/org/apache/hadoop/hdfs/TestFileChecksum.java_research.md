# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileChecksum.java

## Purpose

`TestFileChecksum.java` is a slow parameterized HDFS checksum suite for replicated and erasure-coded files. The complete 830-line file was read. It compares MD5-of-CRC and composite CRC behavior over whole files, byte ranges, striped layouts, missing data blocks, reconstruction failures, mixed bytes-per-checksum blocks, and reconstruction cleanup failure paths.

## Important APIs, Types, and Functions

Key APIs are `FileSystem.getFileChecksum(Path)` and `getFileChecksum(Path,int)`, `ChecksumCombineMode.MD5MD5CRC`, `ChecksumCombineMode.COMPOSITE_CRC`, `StripedFileTestUtil.getDefaultECPolicy`, `DistributedFileSystem.setErasureCodingPolicy`, `DFSClient.getLocatedBlocks`, `DataNodeFaultInjector`, `LocatedBlock`, and `DatanodeInfo`. `setup` creates enough DataNodes for data plus parity plus extras, enables block access tokens, configures combine mode, and prepares `/striped`. Helpers include `testStripedFileChecksum`, `testStripedFileChecksumWithMissedDataBlocksRangeQuery`, `getFileChecksum`, `prepareTestFiles`, `shutdownDataNode`, and `getDataNodeToKill`.

## Control Flow

Each parameterized test initializes a fresh cluster for one combine mode. The first group writes identical striped files and compares checksums for ranges around zero, stripe, cell, block-group, and full-file boundaries. Replicated-versus-striped tests assert equality only for composite CRC. Missing-block tests kill a DataNode hosting part of the first block group, compute checksum through reconstruction, restart the DataNode, and compare with normal checksums. Twenty range-query tests cover sizes from 1 byte through twice file size, including small files. Reconstruction failure injects an IOException on the first reconstruction task and expects retry through another DataNode. Mixed bytes-per-checksum verifies composite CRC can combine blocks with different CRC chunk sizes while MD5MD5CRC throws.

## State and Persistence Behavior

State includes per-test MiniDFSCluster files, EC policy on `/striped`, DataNode liveness, block access tokens, and injected global `DataNodeFaultInjector` state restored in `finally`.

## Dependencies and Integration Points

The suite integrates striped block checksum helpers, EC reconstruction, block tokens, file checksum combine modes, DataNode shutdown/restart, and DFSClient located-block selection.

## Risks and Edge Cases

Risks include checksum range normalization past EOF, inconsistent composite CRC across block sizes/layouts, leaked reconstruction state after initialization failure, and global fault injector not restored.

## Test Signals

Signals are equality or inequality of `FileChecksum` objects by combine mode, expected IOException for MD5 with mixed bytes-per-checksum, expected exception when too many DataNodes are down, restart of killed DataNodes, and 90-second timeouts for slow checksum paths.
