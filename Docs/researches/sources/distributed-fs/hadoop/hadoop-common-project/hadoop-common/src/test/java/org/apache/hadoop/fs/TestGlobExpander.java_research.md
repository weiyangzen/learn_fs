# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobExpander.java

Purpose: tests brace expansion behavior in `GlobExpander`, especially expansion around path separators and escaped braces/slashes.

Important APIs/types/functions: `GlobExpander.expand(String)` returns `List<String>`. Helpers `checkExpansionIsIdentical` and `checkExpansion` compare ordered expansions against expected strings.

Control flow/state/persistence: tests are pure and stateless. `testExpansionIsIdentical` feeds malformed, escaped, or non-expandable patterns and expects the original string. `testExpansion` exercises expandable braces, nested braces that must be preserved, suffix/prefix concatenation, escaped slash handling, and multi-alternative paths.

Dependencies/integration points: depends only on the Hadoop glob expander and JUnit. It is an input-level companion to `FileSystem.globStatus` and `GlobPattern`; no filesystem IO occurs.

Risks/test signals: protects against over-expanding nested braces, treating escaped characters as syntax, or changing expansion order. The expected list order is significant because downstream glob processing may rely on deterministic expansion.
