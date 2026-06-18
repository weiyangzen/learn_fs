<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellGenericOptions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellGenericOptions.java

## Purpose
This focused test verifies that Hadoop generic command-line options correctly configure `FsShell` when running HDFS commands. It checks `-fs`, `-conf`, and `-D fs.defaultFS=...` by creating `/data` in a `MiniDFSCluster`.

## Important APIs, Types, and Functions
- `MiniDFSCluster.Builder` creates the target HDFS cluster.
- `FileSystem.getDefaultUri(conf)` supplies the NameNode URI used in generic options.
- `FsShell` and `ToolRunner.run` execute `-mkdir /data`.
- `DFSUtilClient.getNNAddress` and `getNNUri` resolve the shell configuration back to a `FileSystem`.
- Helper methods `testFsOption`, `testConfOption`, `testPropertyOption`, and `execute` mutate the same argument array and verify side effects.

## Control Flow
`testDFSCommand` starts a cluster, obtains its NameNode URI, initializes a four-element argument array with command slots `-mkdir /data`, and runs the three generic option variants. `testConfOption` writes a temporary `hdfs-site.xml` containing `fs.defaultFS`, then invokes the same command path. `execute` runs the shell, resolves a filesystem from the shell configuration, asserts `/data` exists, and deletes it for the next variant.

## State and Persistence Behavior
Cluster state is short-lived and shut down in `finally`. The `/data` directory is created and removed for each option variant. `testConfOption` writes `build/test/minidfs/hdfs-site.xml` and deletes both the file and containing directory afterwards.

## Dependencies and Integration Points
The test bridges Hadoop generic options, `FsShell`, XML configuration loading, HDFS URI resolution, and `FileSystem` creation. It validates the command-line contract between `ToolRunner`, `Configured` tools, and HDFS shell commands.

## Risks
`execute` catches exceptions and prints stack traces without failing directly, so an exception before the assertion path may be masked unless a later assertion fails. The temporary config directory uses a fixed path, making parallel execution susceptible to directory-exists or cleanup races. The mutable shared `args` array is concise but easy to break if new command variants are added.

## Test Signals
The key signal is direct verification that `/data` exists after each generic option style and is removable before the next invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellGenericOptions.java -->
