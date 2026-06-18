<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CacheAdminCmdExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CacheAdminCmdExecutor.java

Purpose: Executes cache-admin command strings for CLI XML tests.
Important APIs/types/functions: `CacheAdminCmdExecutor` extends `CommandExecutor`, stores `namenode` and `CacheAdmin`, and overrides `execute(String)`.
Control flow: Execution converts a command string into argv with `getCommandAsArgs(cmd, "NAMENODE", namenode)` then calls `ToolRunner.run(admin, args)`.
State and persistence behavior: State is the configured NameNode replacement string and reusable `CacheAdmin` tool instance; no persistence beyond HDFS operations performed by the admin command.
Dependencies and integration points: Used by `TestCacheAdminCLI`; depends on `CommandExecutor` result capture and Hadoop `ToolRunner`.
Risks and edge cases: Argument parsing must preserve quoting and placeholder substitution. A reused admin instance carries its configuration between commands.
Test signals: Signals are exit codes and captured stdout/stderr in cache-admin XML tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CacheAdminCmdExecutor.java -->
