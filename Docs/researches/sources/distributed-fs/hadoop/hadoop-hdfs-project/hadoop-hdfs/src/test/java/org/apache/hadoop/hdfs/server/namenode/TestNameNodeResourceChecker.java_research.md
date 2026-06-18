# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourceChecker.java

Purpose: Verifies NameNode disk/resource checking, low-resource safe mode transitions, duplicate volume de-duplication, manually checked volumes, and required versus redundant volume policy behavior.

Important APIs and types: Main APIs under test are `NameNodeResourceChecker.hasAvailableDiskSpace`, `getVolumesLowOnSpace`, `setVolumes`, and `setMinimumReduntdantVolumes`. It also touches `FSNamesystem.NameNodeResourceMonitor` and `NameNodeResourceChecker.CheckedVolume`. `MockNameNodeResourceChecker` is injected into the namesystem resource checker slot.

Control flow: Setup configures an edits directory under a test directory. Simple tests set `DFS_NAMENODE_DU_RESERVED_KEY` to zero or `Long.MAX_VALUE` to force available and unavailable outcomes. The resource monitor test starts a cluster with a one millisecond resource check interval, replaces the checker with a controllable mock, scans live threads for the monitor, then waits for safe mode enter and leave. Volume tests configure multiple name dirs or checked volumes on the same filesystem and assert one physical volume check. The policy test replaces the internal volume map with Mockito `CheckedVolume` instances and flips their availability.

State and persistence behavior: State is runtime-only: resource availability gates safe mode and volume maps inside the checker. Test directories are local filesystem artifacts, not NameNode persisted namespace data.

Dependencies and integration points: Integrates HDFS config keys, MiniDFSCluster, FSNamesystem resource monitoring, Mockito volume mocks, PathUtils test directories, and thread inspection. It validates the path from checker status to NameNode safe mode.

Risks: Thread-name matching and sleep/wait loops can be fragile under slow hosts. Tests that assume two configured paths share a volume depend on local test directory layout. Mocked volume maps bypass path normalization and focus purely on policy.

Test signals: Passing requires correct available/unavailable decisions, safe mode toggling on resource changes, duplicate same-volume checks collapsed to one entry, and required volumes immediately causing resource unavailability when low.
