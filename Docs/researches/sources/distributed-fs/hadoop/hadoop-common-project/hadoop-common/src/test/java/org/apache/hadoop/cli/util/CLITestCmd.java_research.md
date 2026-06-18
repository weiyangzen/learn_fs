# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestCmd.java

Purpose: concrete immutable CLI command record used by the XML parser and test runner.

Important APIs/fields: final `CLICommandTypes type`, final `String cmd`; constructor; `getExecutor`, `getType`, `getCmd`, and `toString`.

Control flow: for `CLICommandFS`, `getExecutor` creates a new `FsShell(conf)` wrapped in `FSCmdExecutor`; unknown command types throw `IllegalArgumentException`.

State and persistence: stores command text and marker type for one parsed test command.

Dependencies/integration: depends on Hadoop `Configuration`, `FsShell`, and `FSCmdExecutor`; constructed by `CLITestHelper.TestConfigFileParser`.

Risks and test signals: each call creates a new `FsShell`, so tests should not assume shell state persists across commands unless Hadoop config/filesystem state carries it. Test unknown type exceptions and string preservation.
