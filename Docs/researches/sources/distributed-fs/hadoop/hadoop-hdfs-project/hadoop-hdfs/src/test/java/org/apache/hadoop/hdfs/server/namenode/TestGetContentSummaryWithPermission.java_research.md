# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetContentSummaryWithPermission.java

**Purpose:** Tests permission enforcement for NameNode `getContentSummary()` over directories and files.

**Important APIs and flow:** `setUp()` starts a `MiniDFSCluster` with block size `1024` and three DataNodes, then stores a `DistributedFileSystem`. `verifySummary()` asserts directory count, file count, and byte length. Tests call `cluster.getNameNodeRpc().getContentSummary(path)` directly and also as a non-superuser through `UserGroupInformation.doAs()`.

**Control flow:** `testGetContentSummarySuperUser()` builds `/fooSuper/barSuper/bazSuper`, creates a 10-byte file, and verifies the superuser can read the same summary even after permissions on the root directory, subdirectory, and file are set to `000`. `testGetContentSummaryNonSuperUser()` builds a similar tree, verifies default `755` directories and `644` file allow summary, then denies summary by removing access from the root directory and subdirectory. It restores directory permissions to `READ_EXECUTE` and confirms file permissions do not affect directory summary traversal.

**State and persistence behavior:** The persistent state is HDFS namespace metadata: directory/file permissions, file length, and content summary counters. No restart is performed. The tests focus on runtime permission checks, not edit-log replay.

**Dependencies and integration points:** Integrates `MiniDFSCluster`, `DistributedFileSystem`, `NameNodeRpcServer.getContentSummary()`, `DFSTestUtil.createFile()`, `FsPermission`, `FsAction.READ_EXECUTE`, and HDFS access-control exceptions.

**Risks and test signals:** The expected behavior is nuanced: directories require read and execute access for non-superusers, but file mode bits inside the tree do not block summary. Passing signals that superuser bypass works, non-superusers are constrained by traversed directories, and content-summary counts remain correct under permission changes.
