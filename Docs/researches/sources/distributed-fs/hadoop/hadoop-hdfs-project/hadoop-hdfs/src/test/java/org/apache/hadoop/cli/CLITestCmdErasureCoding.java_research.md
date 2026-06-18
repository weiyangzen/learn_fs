<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdErasureCoding.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdErasureCoding.java

Purpose: Adds erasure-coding admin command execution to the XML CLI test framework.
Important APIs/types/functions: `CLITestCmdErasureCoding` extends `CLITestCmd`; `getExecutor()` recognizes `CLICommandErasureCodingCli` and returns `ErasureCodingCliCmdExecutor` wrapping `ECAdmin`.
Control flow: The XML parser supplies an erasure-coding command type, and execution dispatches to `ECAdmin` through a command executor. Non-EC command types use base behavior.
State and persistence behavior: No persistence. Runtime state is the inherited command string/type and the per-call `ECAdmin` instance.
Dependencies and integration points: Used by `TestErasureCodingCLI` for `<ec-admin-command>` XML entries and depends on `org.apache.hadoop.hdfs.tools.ECAdmin`.
Risks and edge cases: Mistyped command type or missing EC policies in the cluster setup will surface as generic executor use or admin failures. The command string placeholder expansion happens outside this class.
Test signals: Signals are XML CLI expectations around `ECAdmin` commands, policy enablement, and exit-code/output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdErasureCoding.java -->
