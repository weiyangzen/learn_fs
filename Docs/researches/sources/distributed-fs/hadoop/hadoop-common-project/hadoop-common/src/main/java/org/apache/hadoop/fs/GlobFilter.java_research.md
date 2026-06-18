# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobFilter.java

Purpose: `GlobFilter` is a `PathFilter` that applies a POSIX-like glob pattern to a path's final name and optionally chains a caller-provided filter.

Important APIs: constructors, `init`, `hasPattern`, and `accept`.

Control flow and state: initialization compiles a `GlobPattern` and stores the user filter. RE2/J `PatternSyntaxException` is wrapped as an `IOException` with the legacy `Illegal file pattern` prefix. `accept` matches only `path.getName()` and then invokes the user filter on the full path.

Dependencies and integration: used by `Globber` for component matching and by callers needing reusable glob-based filtering.

Risks: matching only the final component is intentional; callers expecting full-path matching must use `Globber`. Null user filters are not guarded here. Pattern syntax compatibility depends on `GlobPattern` and RE2/J.

Test signals: wildcard detection, name-only matching, user filter chaining, illegal pattern wrapping, brace/character class behavior, and null-filter expectations.
