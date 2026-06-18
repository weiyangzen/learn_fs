# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSMkdirs.java

Purpose: This class tests HDFS directory creation behavior for recursive `mkdirs`, single-level `mkdir`, and NameNode RPC rejection of non-canonical paths.

Important APIs/types/functions: `FileSystem.mkdirs`, `DistributedFileSystem.mkdir`, `NamenodeProtocols.mkdirs`, `ParentNotDirectoryException`, `FileNotFoundException`, `InvalidPathException`, `FsPermission`, `MiniDFSCluster`, and `DFSTestUtil.writeFile`.

Control flow: `testDFSMkdirs` creates `/test/mkdirs`, confirms idempotent `mkdirs`, writes a file below it, and verifies `mkdirs` fails when asked to create a subdirectory under that file. `testMkdir` uses the non-recursive DFS API: root-level creation succeeds, a parent that is a file yields `ParentNotDirectoryException`, and a missing parent yields `FileNotFoundException`. `testMkdirRpcNonCanonicalPath` starts a NameNode-only cluster and directly calls NN RPC with paths containing duplicate slashes, `..`, or `.` components, expecting `InvalidPathException`.

State and persistence behavior: The tests create and delete real namespace entries but no meaningful block data except a small file used as a non-directory parent. Clusters are temporary and shut down after each test.

Dependencies and integration points: Coverage spans the public FileSystem API, DFS-specific `mkdir`, and low-level NamenodeProtocols validation, ensuring client-side canonicalization is not the only defense.

Risks and test signals: The signal is exception specificity and final path existence. Risk is low, but path-normalization behavior is easy to break if validation moves between client and server layers.
