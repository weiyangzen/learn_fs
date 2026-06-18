# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Name.java

Purpose: implements `find` basename matching expressions `-name` and `-iname`.

Important APIs and types: static `registerExpression()`, constructor, private case-sensitivity constructor, `addArguments()`, `prepare()`, `apply()`, and nested `Iname` filter.

Control flow: one pattern argument is consumed. `prepare()` lowercases the pattern for insensitive mode and builds a `GlobPattern`. `apply()` obtains `getPath(item).getName()`, lowercases when needed, and returns `PASS` on glob match or `FAIL` otherwise.

State and persistence: stores `GlobPattern` and case-sensitivity flag after preparation; no mutation.

Dependencies and integration: extends `BaseExpression`, uses Hadoop `GlobPattern`, `PathData`, and `StringUtils.toLowerCase()`. `Iname` wraps `new Name(false)` through `FilterExpression`.

Risks: matching is basename-only, not full path. Case-insensitive behavior lowercases with Hadoop utility, so locale expectations should be checked. `globPattern` is null before `prepare()`, so lifecycle is required.

Test signals: cover case-sensitive and insensitive matching, glob metacharacters, basename-only behavior, missing pattern argument, prepare-before-apply requirement, and registration aliases.
