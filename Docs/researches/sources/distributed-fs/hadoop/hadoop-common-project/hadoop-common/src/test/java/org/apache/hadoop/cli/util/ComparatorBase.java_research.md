# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorBase.java

Purpose: abstract base class for CLI output comparators.

Important APIs: no-op constructor and abstract `compare(String actual, String expected)`.

Control flow: instantiated reflectively by `CLITestHelper.compareTestOutput`; subclasses implement exact, line, regexp, substring, token, or cross-output matching.

State and persistence: stateless by contract.

Dependencies/integration: comparator class names are specified in XML and resolved under `org.apache.hadoop.cli.util`.

Risks and test signals: base documentation says null inputs should return false, but several subclasses do not null-check. Tests should include comparator null-handling or document that XML/runtime never passes null.
