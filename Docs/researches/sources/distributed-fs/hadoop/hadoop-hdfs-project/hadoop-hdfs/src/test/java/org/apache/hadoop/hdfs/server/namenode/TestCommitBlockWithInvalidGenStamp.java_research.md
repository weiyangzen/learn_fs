# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCommitBlockWithInvalidGenStamp.java

Purpose: Cluster-level regression test that the NameNode rejects file completion when the client submits a last block with a generation stamp that does not match NameNode state.

Important APIs/types/functions: Uses `MiniDFSCluster`, `DistributedFileSystem`, `FSDirectory`, `DFSTestUtil.addBlockToFile`, `ExtendedBlock`, and client protocol `complete`.

Control flow: The test creates `/file`, obtains its `INodeFile`, injects a block, clones it, mutates the submitted `ExtendedBlock` generation stamp to `123`, and calls `complete`. It expects an `IOException`, then retries completion with the correct block and expects success.

State and persistence behavior: Targets in-memory NameNode block map and under-construction file state. Restart persistence is not tested.

Dependencies and integration points: Exercises real DFS client-to-NameNode completion flow, including client identity, file ID, block pool ID, and block generation-stamp checking.

Risks: The test is sensitive to exact error text and to `DFSTestUtil.addBlockToFile` staying aligned with NameNode block construction.

Test signals: Expected exception text includes `Commit block with mismatching GS`; correct completion returns true.
