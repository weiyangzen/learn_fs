<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdDFS.java

Purpose: Adds DFSAdmin support to the generic XML CLI test command abstraction.
Important APIs/types/functions: `CLITestCmdDFS` extends `CLITestCmd`; `getExecutor(String, Configuration)` recognizes `CLICommandDFSAdmin` and returns `FSCmdExecutor` with a `DFSAdmin` tool.
Control flow: The parser-created command keeps its raw string and command type. At execution time, matching DFSAdmin types are routed to `DFSAdmin`; all other command types fall back to the base command executor.
State and persistence behavior: No durable state; it stores command text/type in the inherited `CLITestCmd` fields and instantiates a fresh `DFSAdmin` per execution.
Dependencies and integration points: Integrated by `CLITestHelperDFS` and HDFS CLI tests that parse `<dfs-admin-command>` elements from XML.
Risks and edge cases: If the XML parser assigns the wrong command type, DFSAdmin commands fall through to generic execution. The executor depends on the caller passing the correct NameNode tag and configuration.
Test signals: Covered indirectly by HDFS CLI XML suites that include DFSAdmin commands and expect output/exit-code matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdDFS.java -->
