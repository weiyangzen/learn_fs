<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockMissingException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockMissingException.java

Purpose: Verifies that deleting the only physical replica of a block causes HDFS reads to fail with `BlockMissingException`.

Important APIs, types, and functions: `MiniDFSCluster`, `DistributedFileSystem`, `FSDataOutputStream`, `FSDataInputStream`, `LocatedBlocks`, `getBlockLocations`, `corruptBlockOnDataNodesByDeletingBlockFile`, and `BlockMissingException`.

Control flow: The test starts a three-DataNode cluster with short client retry windows, creates a four-block file with replication factor one, asks the NameNode for block locations, deletes the first block file on the DataNode, then attempts to read the file sequentially. `validateFile` reads until EOF or exception and asserts that `BlockMissingException` was observed.

State and persistence behavior: The key state is on-disk block storage in the MiniDFSCluster's DataNode directories and NameNode block-location metadata. The test physically deletes the block file through cluster test utilities but does not wait for block reports; it relies on the client discovering the missing replica during read.

Dependencies and integration points: Exercises client read retry/error translation, NameNode block location lookup, DataNode storage files, and the cluster's block corruption/deletion test hooks.

Risks: If missing-block detection behavior changes from read-time exception to earlier metadata reporting, the test may need adjustment. The file creation helper writes zero-filled blocks, so this is an availability/error-path test rather than a content integrity test.

Test signals: Success means the client read path sees an unrecoverable missing block and raises `BlockMissingException` instead of silently returning EOF, another exception, or stale data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockMissingException.java -->
