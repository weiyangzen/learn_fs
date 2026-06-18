# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/find/TestIname.java

Purpose: Tests case-insensitive name matching for the `-iname` find expression implemented as `Name.Iname`.

Important APIs/types/functions: `Name.Iname`, `Expression.addArguments` through `TestHelper.addArgument`, `FindOptions`, `prepare`, `apply`, `PathData`, `Result`.

Control flow: Each test resets the mock FS, configures a `Name.Iname` expression with an argument, sets options, calls `prepare`, creates a `PathData` with a leaf filename, and applies the expression. Cases cover exact same-case match, non-match, mixed-case match, glob match with `n*e`, mixed-case glob match, and glob non-match.

State/persistence: Uses reset static mock filesystem and in-memory expression state derived from the pattern argument.

Dependencies/integration: Integrates `PathData` name extraction with find glob/pattern logic and case-insensitive matching.

Risks: Only leaf-name matching is covered; no explicit tests for path separators, empty names, escaped glob characters, or locale-specific case behavior.

Test signals: `Result.PASS`/`Result.FAIL` equality for exact and glob patterns independent of case.
