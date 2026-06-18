# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestNodeFencer.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestNodeFencer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestNodeFencer.java

Purpose: this test validates parsing and execution sequencing for `NodeFencer` configurations, including custom fencer classes, comments/whitespace, no-argument methods, and short-name aliases for shell and SSH fencing.

Important APIs and types: `setupFencer()` builds a `NodeFencer` from a raw configuration string. Nested `AlwaysSucceedFencer` and `AlwaysFailFencer` implement `FenceMethod`, record static call counts, last fenced target, and arguments. Tests use a mocked `HAServiceTarget`.

Control flow: setup resets static mock fencer state and target behavior. Single and multiple fencer tests verify first success stops the chain. Whitespace/comment tests verify ignored lines and fallback from failing to succeeding fencer. Short-name tests resolve `shell` and `sshfence` forms; SSH variants return false in this environment rather than throwing.

State and persistence: state is in static counters and argument lists on the nested fencer classes. No files or network state are required except platform shell behavior for the shell alias.

Dependencies and integration points: integrates `NodeFencer`, `FenceMethod`, Hadoop `Configuration`, `Configured`, platform detection through `Shell.WINDOWS`, and short-name resolution to `ShellCommandFencer`/`SshFenceByTcpPort`.

Risks: static fencer state must be cleared before each test. Shell alias success differs between Windows and Unix, hence the platform-specific command constants.

Test signals: validates config parsing, arg extraction including null arg, ordered fallback semantics, comment stripping, target propagation, and alias recognition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestNodeFencer.java -->
