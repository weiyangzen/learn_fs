# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHDFSConcat.java

**Purpose:** Integration tests for HDFS `concat`, covering block transfer into the target inode, source deletion, content ordering, edit-log replay, quota accounting, path validation, reserved paths, snapshots/inode references, and permission enforcement.

**Important APIs and flow:** `startUpCluster()` creates a two-DataNode `MiniDFSCluster` with 512-byte block size, exposes `DistributedFileSystem` and `NamenodeProtocols`, and teardown closes both. Tests create files with `DFSTestUtil`, call `dfs.concat(target, sources)`, inspect `HdfsFileStatus`, `LocatedBlocks`, `ContentSummary`, and exceptions, and sometimes use alternate `UserGroupInformation` filesystems.

**Control flow:** `testConcat()` concatenates ten full files and one small file, verifies block count, length, source removal, recreated source names, and byte ordering. `testConcatInEditLog()` restarts the NameNode and checks replay preserves target existence and modification time. Negative tests cover different directories, nonexistent sources, empty source lists, larger preferred source block size, reserved raw paths, same source/target inode reference, permission enabled/disabled behavior, and separate read/write permission failures. Quota tests verify concat may decrease or increase consumed space depending on source/target replication and can throw `QuotaExceededException`.

**State and persistence behavior:** Concat mutates namespace state by moving source blocks into the target inode and deleting source inodes; edit-log replay is explicitly checked. Quota namespace and disk-space counts are expected to update atomically with the concat. Snapshot/reference coverage ensures source-target identity checks are based on inode identity, not only path text.

**Dependencies and integration points:** Integrates `DistributedFileSystem.concat()`, NN RPCs, `FSDirectory`, edit logs, block locations, quotas, snapshots, `RemoteException`, `AccessControlException`, and permission configuration (`DFS_PERMISSIONS_ENABLED_KEY`).

**Risks and test signals:** Concat is sensitive to block layout and quota math. Passing signals the user-visible API preserves byte order, removes sources, persists across restart, rejects invalid path/layout cases, and enforces permissions and quotas consistently.
