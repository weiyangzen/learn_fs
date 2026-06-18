# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/FSCmdExecutor.java

Purpose: executes parsed CLI commands through Hadoop `FsShell`.

Important APIs/fields: `namenode`, `FsShell shell`, constructor, and `execute`.

Control flow: `execute` tokenizes command text using inherited `getCommandAsArgs(cmd, "NAMENODE", namenode)` and invokes `ToolRunner.run(shell, args)`.

State and persistence: holds the shell instance and namenode replacement for the executor instance. Filesystem mutations are performed by the invoked `FsShell` commands.

Dependencies/integration: created by `CLITestCmd` for `CLICommandFS`; depends on Hadoop `FsShell` and `ToolRunner`.

Risks and test signals: shell reuse within an executor may carry configuration but not across command objects; placeholder substitution must produce valid FsShell arguments. Tests should verify quoted arguments and expected exit codes for representative FsShell commands.
