# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallerContext.java

## Purpose
`TestCallerContext` verifies construction of caller context strings, key/value append behavior, append-if-absent semantics, and separator validation.

## Important APIs, Types, and Functions
The tests use `CallerContext.Builder`, `CallerContext.getContext()`, and configuration key `HADOOP_CALLER_CONTEXT_SEPARATOR_KEY`. They exercise `append(String)`, `append(String, String)`, `appendIfAbsent(String, String)`, and `build()`.

## Control Flow
Tests configure `$` as the separator, append raw context entries and key/value entries, split the resulting context, and verify expected order. `appendIfAbsent` first refuses to replace an existing key, then appends missing keys including a key that is a substring of existing keys. The final test sets a tab separator and expects `IllegalArgumentException` during build.

## State and Persistence
State is local to the builder and resulting `CallerContext`. No filesystem or global state is persisted.

## Dependencies and Integration Points
Caller contexts are propagated through Hadoop IPC for audit and tracing. This test protects separator parsing and duplicate-key behavior configured through core-site keys.

## Risks and Edge Cases
The separator can itself appear in appended values; the test documents the raw concatenation behavior by appending `$$`. Append-if-absent must match whole keys, not substrings.

## Test Signals
Signals are exact context strings, correct number of separated items, preservation of original key values, append of substring keys as distinct entries, and rejection of illegal separators.
