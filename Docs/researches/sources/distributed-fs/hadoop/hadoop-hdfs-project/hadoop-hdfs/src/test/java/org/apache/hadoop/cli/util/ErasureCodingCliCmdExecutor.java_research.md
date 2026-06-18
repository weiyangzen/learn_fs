<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/ErasureCodingCliCmdExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/ErasureCodingCliCmdExecutor.java

Purpose: Executes erasure-coding admin command strings for CLI XML tests.
Important APIs/types/functions: `ErasureCodingCliCmdExecutor` extends `CommandExecutor`, stores `namenode` and `ECAdmin`, and overrides `execute(String)`.
Control flow: It converts command text to argv using `NAMENODE` replacement and invokes `ToolRunner.run(admin, args)`.
State and persistence behavior: Local state is only the admin tool and NameNode string; persistent effects are EC policy settings in the MiniDFSCluster namespace.
Dependencies and integration points: Used by `CLITestCmdErasureCoding` in `TestErasureCodingCLI`.
Risks and edge cases: ECAdmin command behavior depends on enabled policies and HDFS cluster capability. Argument parsing must align with XML expectations.
Test signals: Signals are CLI XML cases around EC policy administration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/ErasureCodingCliCmdExecutor.java -->
