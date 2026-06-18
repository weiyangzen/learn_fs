# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorData.java

Purpose: mutable data holder for one expected CLI validation and its actual result.

Important APIs/fields: `expectedOutput`, `actualOutput`, `testResult`, `exitCode`, `comparatorType`, with getters and setters.

Control flow: parser fills comparator type, expected output, and optional expected exit code; runner updates actual output, actual exit code, and boolean result after command execution.

State and persistence: in-memory test state only.

Dependencies/integration: consumed by `CLITestHelper.compareTestOutput`, `compareTextExitCode`, and result display.

Risks and test signals: `exitCode` is overwritten with actual exit code after comparison, so post-run display cannot directly show expected exit code. Tests should verify failure diagnostics remain useful and initial default `-1` means no exit-code check.
