# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestVersionUtil.java

Purpose: Compatibility tests for `VersionUtil.compareVersions()`, especially Maven-like comparable-version ordering. It verifies equality normalization, numeric ordering, qualifier ordering, alpha shorthand normalization, and snapshot-versus-release precedence.

Important APIs/types/functions: `testCompareVersions()` contains the matrix of equality and ordering assertions. Helper `assertExpectedValues(String lower, String higher)` asserts both forward negative and reverse positive comparisons.

Control flow: The test first asserts equal pairs such as `1`, `1.0`, and `1.0.0`, plus alpha spellings like `alpha-1`, `a1`, and `alpha1`. It then runs ordered pairs spanning numeric version increments, multi-digit numeric comparison, alphabetic suffixes, alpha/beta qualifiers, and `SNAPSHOT` versions.

State and persistence behavior: Stateless comparison contract with no external state. The comparison algorithm's parsed-token semantics are the implicit persistent compatibility surface because Hadoop components may gate features or compatibility based on version ordering.

Dependencies and integration points: Depends on Hadoop `VersionUtil` and JUnit. The comments explicitly align behavior with Maven `ComparableVersion`, which is relevant for dependency and Hadoop component version comparisons.

Risks: Version comparison is notoriously subtle; the test covers many common forms but not every Maven qualifier (`rc`, `milestone`, timestamped snapshots, build metadata). The alpha shorthand behavior is delicate: `1.a` is greater than `1.0`, while `1.a0`/`1a0` are treated as alpha-zero and lower than `1.0`.

Test signals: Symmetric lower/higher assertions and equality normalization protect against tokenization, numeric-vs-lexical comparison, and snapshot precedence regressions.
