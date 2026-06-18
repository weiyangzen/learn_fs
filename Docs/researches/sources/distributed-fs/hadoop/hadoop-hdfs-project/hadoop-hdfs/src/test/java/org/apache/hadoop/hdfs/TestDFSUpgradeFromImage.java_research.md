# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgradeFromImage.java

Purpose: upgrades archived historical HDFS image/data directories, verifies file checksums and namespace shape, tests reserved-path migrations, checks corrupt image rejection, and ensures edit logs remain available through inotify after upgrade.

Important APIs and types: `MiniDFSCluster`, `StartupOption.UPGRADE`, `FSImageFormat`, `FSImageTestUtil`, `IllegalReservedPathException`, `DFSInotifyEventInputStream`, `EventBatch`, `DirectoryListing`, `HdfsFileStatus`, `CRC32`, `FileUtil.unTar`, and `ClusterVerifier`.

Control flow: `unpackStorage` extracts a tarred DFS image and loads reference checksums. `upgradeAndVerify` starts an unmanaged upgrade cluster, waits for safe mode exit, recursively recovers leases, verifies file contents, and optionally invokes a verifier. Reserved-path tests set rename pairs, list the namespace before and after finalize/restart, and compare expected paths. Corrupt MD5 modifies VERSION files and checks startup failure. `testPreserveEditLogs` consumes expected create/close/rename/unlink inotify events from preserved edits.

State and persistence: unpacks historical NN/DN storage under test directories, reads checksum manifests, mutates fsimage rename-reserved settings, finalizes clusters, restarts NameNode, recovers leases, and reads edit-log-backed inotify streams.

Dependencies and integration: integrates upgrade storage loading, FSImage compatibility, reserved namespace protection, lease recovery, DFSClient listings, block reads, and inotify event reconstruction.

Risks: depends on external test tarballs and checksum text order, sleeps/retries lease recovery, static reserved rename pairs can leak if not reset by framework, and inotify expectations are tightly bound to fixture edit order.

Test signals: exact per-file CRCs and overall CRC, expected startup failures/messages, expected renamed paths and counts, lease recovery success, preserved inotify event types/paths/txids, and null polling past the last edit.
