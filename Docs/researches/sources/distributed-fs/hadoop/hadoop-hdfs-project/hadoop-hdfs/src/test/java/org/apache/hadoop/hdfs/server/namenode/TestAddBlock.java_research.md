<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlock.java

Purpose: tests that AddBlock edit-log operations are written and replayed correctly for complete files and an under-construction append.

Important APIs/types/functions: uses `MiniDFSCluster`, `DFSTestUtil.createFile()`, `DistributedFileSystem`, `FSDataOutputStream`, `DFSOutputStream.hsync(UPDATE_LENGTH)`, `FSDirectory`, `INodeFile`, `BlockInfo`, and `BlockUCState`.

Control flow: setup starts a three-DataNode cluster with 1 KiB block size. `testAddBlock()` creates files with lengths around one and two block boundaries, restarts the NameNode, then inspects inode block arrays for count, length, and `COMPLETE` state. `testAddBlockUC()` appends without closing, hsyncs length, restarts, and verifies the original block is complete while the new block is `UNDER_CONSTRUCTION`.

State and persistence: block metadata is persisted through edit logs and replayed on NameNode restart. The under-construction block retains UC state after restart.

Dependencies and integration points: covers client create/append, edit-log add-block replay, inode block metadata, and lease/under-construction behavior.

Risks and test signals: risks include off-by-one block lengths, losing UC state, or replaying wrong block counts. Signals are direct assertions on `INodeFile.getBlocks()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlock.java -->
