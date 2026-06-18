# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandFS.java

Purpose: marker class identifying filesystem shell commands in the CLI test harness.

Important APIs/types: implements `CLICommandTypes` without additional fields or methods.

Control flow: `CLITestCmd.getExecutor` checks `getType() instanceof CLICommandFS` and returns an `FSCmdExecutor`.

State and persistence: stateless marker.

Dependencies/integration: integrates XML `<command>` elements with `FsShell` execution in Hadoop Common tests.

Risks and test signals: behavior depends on `instanceof` rather than enum identity, so subclassing would also route to `FSCmdExecutor`. Tests should confirm parser-created commands use this type.
