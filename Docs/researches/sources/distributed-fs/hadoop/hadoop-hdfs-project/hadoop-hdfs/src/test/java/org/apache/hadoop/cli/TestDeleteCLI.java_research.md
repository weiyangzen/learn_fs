<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestDeleteCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestDeleteCLI.java

Purpose: Runs delete CLI XML tests with HDFS safe-delete thresholds.
Important APIs/types/functions: `TestDeleteCLI` extends `CLITestHelperDFS`; key methods are `setUp()`, `tearDown()`, `getTestFile()`, `expandCommand()`, `execute()`, and `testAll()`.
Control flow: Setup fixes replication to 1, sets `HADOOP_SHELL_SAFELY_DELETE_LIMIT_NUM_FILES` to 5, starts a one-Datanode cluster, and executes expanded commands from `testDeleteConf.xml`.
State and persistence behavior: State is transient namespace content created and removed by XML commands. The NameNode URI is captured for placeholder expansion.
Dependencies and integration points: Depends on shell/FS delete command behavior, HDFS cluster semantics, and the DFS CLI helper parser.
Risks and edge cases: Safe-delete behavior is threshold-sensitive. The two-second teardown sleep suggests prior cleanup races. Output can vary if replication or trash defaults change.
Test signals: Signals are XML cases for delete, recursive delete, and safe-delete prompting/limits against HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestDeleteCLI.java -->
