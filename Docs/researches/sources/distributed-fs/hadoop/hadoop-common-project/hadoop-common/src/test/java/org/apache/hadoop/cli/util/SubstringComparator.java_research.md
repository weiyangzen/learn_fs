# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/SubstringComparator.java

Purpose: comparator that passes when expected appears anywhere in actual output.

Important APIs: `compare` uses `actual.indexOf(expected)`.

Control flow: returns false for `-1`, true otherwise.

State and persistence: stateless.

Dependencies/integration: reflectively loaded by CLI XML tests.

Risks and test signals: no null handling and no normalization; case-sensitive and whitespace-sensitive. Tests should include expected substrings with path separators and platform line endings.
