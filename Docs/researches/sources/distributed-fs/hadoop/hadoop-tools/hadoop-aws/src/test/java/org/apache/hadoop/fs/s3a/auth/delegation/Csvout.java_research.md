<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/Csvout.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/Csvout.java

## Purpose

`Csvout` is a small test utility for writing delimited rows, used by delegation-token load tests to record timing outcomes. It is closer to TSV/CSV line writing than a full CSV implementation.

## Important APIs, Types, and Functions

- Constructor takes a `Writer`, field separator, and end-of-line string.
- `write(Object)` writes a single field, adding the separator unless at the start of a line.
- `write(Object...)` writes multiple fields in order.
- `newline()` writes the configured EOL and resets line-start state.
- `close()` closes the wrapped writer.

## Control Flow and State

The only internal state is `isStartOfLine`. It starts true, flips false after the first field, and resets true on `newline()`. `write(Object...)` loops through fields and delegates to `write(Object)`.

## State and Persistence Behavior

Persistence is delegated to the supplied `Writer`, typically a `FileWriter` in `ILoadTestSessionCredentials`. The class does not flush explicitly and does not own escaping or quoting policy.

## Dependencies and Integration Points

It uses only `java.io.Closeable`, `IOException`, and `Writer`. Load-test outcomes call it through a fluent `write(...).newline()` API.

## Risks and Edge Cases

It does not escape separators, EOLs, quotes, or null objects. Callers must pre-quote strings and avoid separator-containing fields. A null field would throw `NullPointerException` via `o.toString()`.

## Test Signals

There are no direct unit tests in this file. It is indirectly tested when load tests produce readable timing files with schema and rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/Csvout.java -->
