<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLI.java

Purpose: Runs the ACL CLI XML suite against an HDFS cluster with ACLs enabled and POSIX ACL inheritance disabled.
Important APIs/types/functions: `TestAclCLI` extends `CLITestHelperDFS`; key methods are `initConf()`, `setUp()`, `tearDown()`, `getTestFile()`, `expandCommand()`, `execute()`, and `testAll()`.
Control flow: Setup initializes CLI helper state, enables NameNode ACLs, starts a one-Datanode cluster, captures NameNode URI and user name, then XML commands from `testAclCLI.xml` are expanded and executed. Teardown closes the FS and cluster.
State and persistence behavior: Cluster namespace and ACL metadata are transient per test. It stores `MiniDFSCluster`, `FileSystem`, `namenode`, and `username` fields for command expansion.
Dependencies and integration points: Integrates NameNode ACL feature flags, the common CLI XML harness, `FileSystem`, and HDFS command executors.
Risks and edge cases: Output expectations depend on username, line separator, and the disabled inheritance policy. Resource cleanup ordering matters because superclass teardown may inspect command results.
Test signals: Signals are `testAll()` XML cases for set/get/remove ACL commands, placeholder expansion, and exit-code/output comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLI.java -->
