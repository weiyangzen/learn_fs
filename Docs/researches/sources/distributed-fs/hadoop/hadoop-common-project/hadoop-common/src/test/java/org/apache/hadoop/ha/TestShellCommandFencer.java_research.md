# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestShellCommandFencer.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestShellCommandFencer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestShellCommandFencer.java

Purpose: this test covers `ShellCommandFencer` command execution, configuration validation, subprocess IO handling, logging, environment variable injection, peer-aware variables, and command abbreviation.

Important APIs and types: a `ShellCommandFencer` is configured with a test property. `TEST_TARGET` is a `DummyHAService`. The test temporarily replaces static `ShellCommandFencer.LOG` with a Mockito logger using `LogAnswer` to delegate real log methods while enabling verification.

Control flow: tests run commands that succeed, return nonzero, or do not exist; construct invalid `NodeFencer` configs for missing shell args; verify stdout maps to info logs and stderr to warn logs; run platform-specific environment echo commands; and verify `read` exits because subprocess stdin is closed. Peer tests set transition target statuses so target/source environment variables are selected by role.

State and persistence: state is process environment built from Hadoop `Configuration` keys and target metadata. No persistent files are written. The static logger is restored in `AfterAll`.

Dependencies and integration points: depends on local shell semantics, Hadoop `Shell`, `NodeFencer` parser, `DummyHAService`, Mockito, and JUnit timeout for subprocess blocking detection.

Risks: shell behavior is platform-dependent, so tests branch on `Shell.WINDOWS`. Logger replacement is static and must be restored to avoid cross-test pollution.

Test signals: confirms exit-code-based fencing result, bad config diagnostics, stdout/stderr log routing with abbreviated command names, configuration-to-env key normalization, target/source host-port variables, closed stdin, and abbreviation boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestShellCommandFencer.java -->
