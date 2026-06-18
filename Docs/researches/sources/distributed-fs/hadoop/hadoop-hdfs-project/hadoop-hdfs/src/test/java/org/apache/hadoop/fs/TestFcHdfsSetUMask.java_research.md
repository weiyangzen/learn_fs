<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsSetUMask.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsSetUMask.java

Purpose: Verifies FileContext umask behavior for HDFS mkdir and create, including recursive parent permissions.
Important APIs/types/functions: `TestFcHdfsSetUMask`, constants for open/blank/user-group permissions and umasks, helpers `testMkdirWithExistingDir()`, `testMkdirRecursiveWithNonExistingDir()`, `testCreateRecursiveWithExistingDir()`, and `testCreateRecursiveWithNonExistingDir()`.
Control flow: Setup starts HDFS with restrictive `fs.permissions.umask`, opens FileContext, and each test sets a specific umask before mkdir/create operations. Assertions compare final file, directory, and parent permissions.
State and persistence behavior: State is the FileContext umask and test-root namespace. Per-test setup resets to wide-open umask and creates the root; teardown deletes it.
Dependencies and integration points: Depends on HDFS permission application, `FileContextTestHelper`, and `FsPermission` semantics.
Risks and edge cases: Parent directory permissions for recursive creation are subtle, especially blank permissions that still need access bits to create children. Umask is mutable on the shared FileContext.
Test signals: Signals are exact `FsPermission` matches for clear/open/middle umasks across existing and non-existing parent scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsSetUMask.java -->
