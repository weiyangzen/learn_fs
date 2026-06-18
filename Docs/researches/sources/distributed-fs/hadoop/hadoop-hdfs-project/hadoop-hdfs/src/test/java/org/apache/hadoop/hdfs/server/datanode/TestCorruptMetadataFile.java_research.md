# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCorruptMetadataFile.java

## Purpose
This file tests DataNode and metadata-header behavior when block checksum metadata files are truncated or corrupt.

## Important APIs, Types, and Functions
- `BlockMetadataHeader.preadHeader` is tested directly for valid, empty, partial, and invalid headers.
- `DFSTestUtil.getFirstBlock` and `MiniDFSCluster#getBlockMetadataFile` locate the real metadata file for a written HDFS block.
- `LambdaTestUtils.intercept` checks for `BlockMissingException` and `CorruptMetaHeaderException`.

## Control Flow and Behavior
The setup creates a one-DataNode cluster builder and reduces client block acquire failures to speed up failure detection. `testReadBlockFailsWhenMetaIsCorrupt` writes and reads a one-byte file successfully, truncates the `.meta` file to zero, expects read failure, then writes eleven invalid bytes and expects another read failure. It waits for the NameNode block manager to count one corrupt block. `testBlockMetaDataHeaderPReadHandlesCorruptMetaFile` writes a valid seven-byte metadata header, reads it successfully, then checks that empty, partial, and invalid seven-byte headers throw corrupt-header exceptions.

## State and Persistence
The tests directly mutate real metadata files on disk with `RandomAccessFile`. The first test changes cluster-visible corruption state in the NameNode block manager.

## Dependencies and Integration Points
The file integrates MiniDFSCluster, DFS client read path, DataNode block metadata files, `BlockMetadataHeader`, NameNode corrupt block tracking, and Hadoop test exception utilities.

## Risks and Edge Cases
Covered edge cases include zero-length metadata, invalid but non-empty metadata, partial valid headers, invalid full-length headers, and client retry behavior with only one DataNode. Direct file mutation requires careful close handling and can be platform-sensitive if metadata file paths change.

## Test Signals
Signals are intercepted `BlockMissingException` on corrupt metadata reads, corrupt block count reaching one, successful parse of a valid header, and intercepted `CorruptMetaHeaderException` for invalid header cases.
