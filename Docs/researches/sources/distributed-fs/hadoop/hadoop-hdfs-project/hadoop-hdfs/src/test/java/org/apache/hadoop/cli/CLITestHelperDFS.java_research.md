<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestHelperDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestHelperDFS.java

Purpose: Specializes the generic CLI XML parser so HDFS tests can include DFSAdmin commands.
Important APIs/types/functions: `CLITestHelperDFS` extends `CLITestHelper`; `getConfigParser()` returns `TestConfigFileParserDFS`; nested `endElement()` handles `dfs-admin-command`.
Control flow: During SAX parsing, closing a `dfs-admin-command` tag appends a `CLITestCmdDFS` to either test or cleanup command lists. Other tags defer to the base parser.
State and persistence behavior: Maintains parser-local `charString` and inherited command lists; no durable state.
Dependencies and integration points: Provides the common base for ACL, delete, HDFS, XAttr, and crypto CLI tests that need both normal shell commands and DFSAdmin commands.
Risks and edge cases: Parser behavior depends on exact XML tag spelling and on inherited list selection. Unknown tags must continue flowing to the superclass.
Test signals: Test signal is successful execution of XML files containing mixed DFSAdmin and base CLI command tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestHelperDFS.java -->
