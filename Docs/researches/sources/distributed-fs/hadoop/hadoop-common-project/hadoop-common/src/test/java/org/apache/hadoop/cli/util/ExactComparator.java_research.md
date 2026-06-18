# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactComparator.java

Purpose: comparator requiring complete actual output equality with expected output.

Important APIs: overrides `compare` as `actual.equals(expected)`.

Control flow: reflectively loaded by comparator type `ExactComparator`; returns true only for identical strings including whitespace and line endings.

State and persistence: stateless.

Dependencies/integration: used by XML CLI tests through `CLITestHelper`.

Risks and test signals: no null checks despite base contract; platform line endings and trailing output make this brittle. Tests should include exact whitespace cases and avoid null actual/expected.
