<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestXAttrCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestXAttrCLI.java

Purpose: Runs XAttr CLI XML tests with NameNode extended attributes enabled.
Important APIs/types/functions: `TestXAttrCLI` extends `CLITestHelperDFS`; methods configure xattrs, expand `NAMENODE` and `#LF#`, execute commands, and call `testAll()`.
Control flow: Setup enables `DFS_NAMENODE_XATTRS_ENABLED_KEY`, installs the HDFS policy provider, forces replication 1, starts one Datanode, and executes XML commands from `testXAttrConf.xml`.
State and persistence behavior: Namespace xattrs are transient. Cluster/FS/NameNode/user fields support command expansion and execution.
Dependencies and integration points: Integrates HDFS xattr feature flags, FS shell xattr commands, service authorization, and the CLI helper.
Risks and edge cases: Output is sensitive to line separators and xattr feature enablement. XML cleanup must remove xattrs/files to avoid cross-case leakage.
Test signals: Signals are XML cases for set/get/remove/list xattrs and expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestXAttrCLI.java -->
