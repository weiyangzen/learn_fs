# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestData.java

Purpose: mutable data holder for one XML-defined CLI test case.

Important APIs/fields: `testDesc`, `testCommands`, `cleanupCommands`, `comparatorData`, `testResult`, with simple getters and setters.

Control flow: populated by `CLITestHelper.TestConfigFileParser`, consumed and mutated by `CLITestHelper.testAll`, and read by `displayResults`.

State and persistence: stores in-memory parsed test state and execution outcome only.

Dependencies/integration: depends on `CLICommand`, `ComparatorData`, and Java `ArrayList`.

Risks and test signals: lists may remain null if XML omits sections, causing runner/display failures. Parser tests should verify all required sections initialize lists and result defaults are understood.
