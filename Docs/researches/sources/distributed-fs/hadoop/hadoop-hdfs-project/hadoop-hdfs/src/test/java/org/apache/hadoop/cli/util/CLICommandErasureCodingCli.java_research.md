<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandErasureCodingCli.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandErasureCodingCli.java

Purpose: Marker type for erasure-coding admin CLI commands.
Important APIs/types/functions: `CLICommandErasureCodingCli` implements `CLICommandTypes`.
Control flow: The EC parser creates this type and `CLITestCmdErasureCoding` routes it to `ECAdmin`.
State and persistence behavior: No state or persistence.
Dependencies and integration points: Used by `TestErasureCodingCLI` and `ErasureCodingCliCmdExecutor`.
Risks and edge cases: Dispatch depends on exact `instanceof` checks.
Test signals: Indirectly covered by EC CLI XML tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandErasureCodingCli.java -->
