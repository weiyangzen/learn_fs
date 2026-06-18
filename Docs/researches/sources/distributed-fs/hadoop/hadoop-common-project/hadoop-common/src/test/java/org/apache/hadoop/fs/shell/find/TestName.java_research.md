# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/find/TestName.java

Purpose: Tests case-sensitive leaf-name matching for the `-name` find expression.

Important APIs/types/functions: `Name`, `TestHelper.addArgument`, `FindOptions`, `prepare`, `PathData`, and `Result`.

Control flow: `setup(String)` constructs and prepares a `Name` expression with a single pattern. Tests apply it to `PathData` paths ending in matching, nonmatching, mixed-case, glob-matching, mixed-case glob, and glob-nonmatching names.

State/persistence: In-memory pattern state only; mock FS is reset before each test for `PathData` construction.

Dependencies/integration: Validates that `Name.apply` uses the final path component and Java/Hadoop glob semantics while preserving case sensitivity.

Risks: Coverage is intentionally narrow: no bracket classes, path roots, empty strings, or multiple arguments. Locale-specific case handling is not relevant because matching is case-sensitive.

Test signals: Exact `Result.PASS` or `Result.FAIL` for string and glob patterns, with mixed-case values failing.
