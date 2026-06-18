# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedUnixGroupsMapping.java

Purpose: tests shell-backed Unix group resolution, especially edge cases around nonexistent users, numeric group names versus unresolved group IDs, command timeout configuration, and integration with the higher-level `Groups` framework.

Important APIs and types: `ShellBasedUnixGroupsMapping`, `GroupMappingServiceProvider`, `Groups`, `Shell.ShellCommandExecutor`, `Shell.ExitCodeException`, `CommonConfigurationKeys.HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_KEY`, `ReflectionUtils`, and `GenericTestUtils.LogCapturer`.

Control flow: nested subclasses override `createGroupExecutor` and `createGroupIDExecutor` to return Mockito shell executors with controlled output and exceptions. The tests verify empty results for nonexistent users, filtering of unresolved numeric group IDs when names cannot be resolved, retention of numeric names when the ID command proves they are actual names, and normal group parsing. Timeout tests instantiate a delayed command subclass and assert configured timeout values for seconds, minutes, and millisecond input. `testFiniteGroupResolutionTime` executes sleep/timeout commands, checks log messages, and verifies that direct mapping returns no groups while the `Groups` wrapper raises `IOException`.

State and persistence: captures static logs from `ShellBasedUnixGroupsMapping.LOG`, clears captured output between phases, and uses real sleep/timeout commands. No durable files are written.

Dependencies and integration points: integrates shell command construction, Hadoop configuration duration parsing, the `Groups` cache/service wrapper, Mockito mocks, JUnit timeouts, and platform-specific sleep commands.

Risks: timeout behavior is timing-sensitive and may vary on slow hosts. Windows command semantics differ. Log-message assertions can be brittle if production logging text changes. Mocked executor output must mirror real command output formats to remain meaningful.

Test signals: covers command failure tolerance, ambiguous numeric group handling, timeout propagation to both name and ID executors, direct versus framework-level error behavior, and successful parsing of multi-line shell output.
