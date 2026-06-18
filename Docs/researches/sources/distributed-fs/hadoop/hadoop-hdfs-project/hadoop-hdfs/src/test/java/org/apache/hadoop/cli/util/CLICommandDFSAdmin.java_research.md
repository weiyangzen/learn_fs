<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandDFSAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandDFSAdmin.java

Purpose: Marker type for DFSAdmin CLI commands in the XML harness.
Important APIs/types/functions: `CLICommandDFSAdmin` implements `CLICommandTypes`.
Control flow: The DFS XML parser attaches this marker, and `CLITestCmdDFS` routes it to `DFSAdmin`.
State and persistence behavior: No state or persistence.
Dependencies and integration points: Used by `CLITestHelperDFS`, HDFS CLI tests, ACL/delete/XAttr/crypto tests.
Risks and edge cases: Incorrect marker assignment causes commands to execute with the wrong tool.
Test signals: Indirectly covered wherever `<dfs-admin-command>` appears in XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandDFSAdmin.java -->
