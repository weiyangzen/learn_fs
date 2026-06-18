# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CommandExecutor.java

Purpose: abstract command execution wrapper that tokenizes command strings, expands placeholders, captures stdout/stderr, and returns a result object.

Important APIs/classes: `getCommandAsArgs`, `executeCommand`, abstract `execute`, and nested immutable `Result` with output, exit code, exception, and executed command.

Control flow: `getCommandAsArgs` regex-tokenizes single-quoted, double-quoted, or non-space arguments, replaces `NAMENODE`, `CLITEST_DATA`, and `USERNAME`, then returns a string array. `executeCommand` redirects `System.out` and `System.err` to a buffer, calls subclass `execute`, captures exceptions as exit code `-1`, and restores streams in `finally`.

State and persistence: temporarily mutates JVM-global stdout/stderr, so parallel tests can interfere. No durable state.

Dependencies/integration: used by `FSCmdExecutor`; depends on `CLITestHelper.TEST_CACHE_DATA_DIR` and Java regex/IO APIs.

Risks and test signals: tokenization is shell-like but incomplete for escapes; `replaceAll` treats placeholders as regex; global stream redirection is not thread-safe. Tests should cover quoting, spaces in test data path, exception capture, and stream restoration.
