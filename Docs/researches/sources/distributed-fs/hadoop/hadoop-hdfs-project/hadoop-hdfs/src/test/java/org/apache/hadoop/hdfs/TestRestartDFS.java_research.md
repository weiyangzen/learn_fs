# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRestartDFS.java

Purpose: validates that HDFS namespace, file contents, root metadata, directory owner/group metadata, and optional service RPC configuration survive two consecutive MiniDFSCluster restarts without formatting.

Important APIs and types: `MiniDFSCluster`, `DFSTestUtil.Builder`, `FileSystem`, `FileStatus`, `Path`, `DFS_NAMENODE_SERVICE_RPC_ADDRESS_KEY`, and JUnit assertions.

Control flow: `runTests` optionally enables a service RPC address, starts a four-DN cluster, creates 20 test files under `/srcdat`, records root and directory status, mutates root owner and directory group, then shuts down. It restarts with `format(false)`, checks files and metadata, records root mtime again, shuts down, and restarts a second time to verify the image written during the first restart is still correct. Two JUnit methods run this with and without service RPC enabled.

State and persistence behavior: explicitly tests fsimage/edit persistence across restarts, including owner/group mutations and root modification time preservation. The second restart checks that the post-restart image/checkpoint is not corrupted.

Dependencies and integration points: integrates MiniDFSCluster restart semantics, NameNode storage formatting flags, FileSystem status APIs, owner mutation, and `DFSTestUtil` file creation/check/cleanup.

Risks and edge cases: does not inspect block placement or replication beyond `DFSTestUtil.checkFiles`. The same `Configuration` object is reused and re-mutated for service RPC address. Failures usually indicate storage image/edit replay regressions.

Test signals: `files.checkFiles` returns true after each restart, root mtime and owner/group values match expectations, directory owner/group values match expectations, and cleanup succeeds after the final restart.
