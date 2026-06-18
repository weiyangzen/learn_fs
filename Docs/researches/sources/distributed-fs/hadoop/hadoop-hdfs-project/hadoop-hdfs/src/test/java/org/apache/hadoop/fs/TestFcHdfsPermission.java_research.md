<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsPermission.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsPermission.java

Purpose: Runs generic FileContext permission tests against HDFS.
Important APIs/types/functions: `TestFcHdfsPermission` extends `FileContextPermissionBase`; overrides `getFileContextHelper()` and `getFileContext()`.
Control flow: A two-Datanode cluster and FileContext are created once, with a user working directory. Base permission tests then operate through the returned HDFS FileContext.
State and persistence behavior: Static `fc`, cluster, and working directory persist for the class; per-test cleanup is inherited.
Dependencies and integration points: Integrates HDFS permissions with `FileContextPermissionBase`.
Risks and edge cases: Permissions depend on cluster/user defaults and base cleanup. The class-local `fc` shadows similarly named base fields, so overrides are essential.
Test signals: Signals are inherited permission, owner/group, and status assertions under HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsPermission.java -->
