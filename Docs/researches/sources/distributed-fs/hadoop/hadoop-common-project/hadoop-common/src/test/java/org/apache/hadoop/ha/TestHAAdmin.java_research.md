# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHAAdmin.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHAAdmin.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHAAdmin.java

Purpose: this test verifies command-line usage and help behavior for `HAAdmin`, using an anonymous subclass that resolves every target to a dummy standby service.

Important APIs and types: the test captures `HAAdmin.errOut` and `HAAdmin.out` in `ByteArrayOutputStream`s, calls `tool.run(args)`, and checks text through `assertOutputContains()`. `resolveTarget()` returns `DummyHAService` bound to a fixed socket.

Control flow: setup initializes the tool and output streams. `testAdminUsage()` runs no args, an unknown bare command, an unknown dash command, and bad arity for `-transitionToActive`, expecting return `-1` and diagnostic text. `testHelp()` checks generic and command-specific help return `0`.

State and persistence: no durable state is touched. Test state is captured output and return codes. Output is reset for each `runTool()` invocation.

Dependencies and integration points: depends on `HAAdmin` command parsing, dummy HA target resolution, Hadoop `Configuration`, and Guava `Joiner` for logging command strings.

Risks: assertions search substrings rather than whole output, which is resilient to formatting changes but still sensitive to key wording. It does not exercise actual HA transitions or target-specific resolution failures.

Test signals: validates user-facing CLI contract for usage, help, bad commands, and argument-count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHAAdmin.java -->
