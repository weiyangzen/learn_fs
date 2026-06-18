# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobPattern.java

Purpose: `GlobPattern` translates POSIX-style glob syntax into an RE2/J regular expression and exposes match/wildcard state.

Important APIs: constructor, `compiled`, static `compile`, `matches`, `set`, `hasWildcard`, and internal `error`.

Control flow and state: `set` scans the glob, appending regex text while tracking open character classes and brace groups. `*` becomes `.` followed by `*` through fallthrough, `?` becomes `.`, braces become non-capturing groups, commas inside braces become alternation, `[!` becomes `[^`, and regex metacharacters not intended as glob syntax are escaped. Unclosed classes/groups and missing escaped chars throw `PatternSyntaxException`.

Dependencies and integration: used by `GlobFilter` and indirectly `Globber`; relies on `com.google.re2j.Pattern` with `DOTALL`.

Risks: subtle fallthrough behavior implements `*` as `.*`; changing it can break glob semantics. Character-class edge cases are partly deferred to the regex compiler. `hasWildcard` drives `Globber` lookup strategy and null-vs-empty semantics.

Test signals: `*`, `?`, braces, commas outside braces, character classes, negated classes, escaped chars, regex metachar escaping, unclosed groups/classes, and `hasWildcard` correctness.
