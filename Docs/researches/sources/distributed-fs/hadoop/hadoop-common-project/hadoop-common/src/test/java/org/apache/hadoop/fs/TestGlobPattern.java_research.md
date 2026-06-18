# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobPattern.java

Purpose: verifies translation and matching semantics of Hadoop glob patterns backed by RE2J.

Important APIs/types/functions: `GlobPattern`, `GlobPattern.compile`, `GlobPattern.matches`, RE2J `PatternSyntaxException`, and helper methods `assertMatch`/`shouldThrow`.

Control flow/state/persistence: tests are pure. Valid cases cover `*`, `?`, character classes, negated classes, escaped metacharacters, brace alternatives, literal closing braces, newline matching, and regex metacharacters that must be literal. Invalid cases require syntax exceptions for unmatched class/brace/escape patterns. A timeout-protected pathological filename guards against expensive regex behavior.

Dependencies/integration points: integrates with RE2J exception behavior and Hadoop path/glob matching. It complements glob expansion and filesystem glob status tests.

Risks/test signals: catches regex injection/literal escaping regressions, invalid pattern acceptance, and performance/pathological backtracking issues. The `@Timeout(10)` on the long history filename is a direct signal for denial-of-service style pattern translation regressions.
