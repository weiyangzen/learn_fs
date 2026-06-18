<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLockReport.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLockReport.java

Purpose: this integration test ensures long namesystem lock reports include meaningful operation context: user, authentication method, client IP, source, destination, and permission status for common filesystem operations.

Important APIs, types, and functions: setup uses `MiniDFSCluster`, `HdfsConfiguration`, `DFSTestUtil.getFileSystemAs`, `UserGroupInformation`, `GenericTestUtils.LogCapturer`, and lock threshold keys set to zero. Two functional interfaces (`SupplierWithException`, `Procedure`) allow a single `testLockReport` helper to wrap operations that return a value or not. `matches` scans captured log lines with regular expressions.

Control flow: setup makes every read/write lock report visible by zeroing thresholds and suppression interval, starts a four-DataNode cluster, creates a test user `bob` in supergroup `hadoop`, and captures `FSNamesystem.LOG`. The main test obtains a filesystem as `bob`, runs create/open/setPermission/setOwner/listStatus/getFileStatus/mkdirs/rename/delete under `userGroupInfo.doAs`, and after each operation asserts one log line matches the expected context regex. Streams returned by create/open are closed by the caller after the assertion.

State and persistence behavior: the persistent state is the HDFS namespace objects created and mutated during the operation sequence (`/file`, `/dir`, rename to `/file2`, delete). The test's target state is transient log output from lock reporting, not fsimage/edit-log persistence.

Dependencies and integration points: depends on RPC/user context propagation into namesystem operations, permission/status formatting, `FSNamesystemLock` long-hold report context capture, log text emitted by `FSNamesystem`, and HDFS client APIs.

Risks and edge cases: regexes are intentionally flexible for IP addresses but strict for operation names and permission strings. Comments for rename/delete are swapped in one area, but assertions use the correct regexes. Setting thresholds to zero makes any implementation change in report emission volume visible. The test can be brittle if permission string formatting changes.

Test signals: captured lock report lines must match per-operation context after each HDFS call. The sequence also verifies context changes after `setPermission` and `setOwner` are reflected in later rename logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLockReport.java -->
