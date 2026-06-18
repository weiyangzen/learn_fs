# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogParser.java

## Purpose
`S3LogParser` provides a named regular expression and ordered group list for parsing AWS S3 server access log lines.

## Important APIs and control flow
Private helpers build named regex groups for simple, date/time, number, and quoted fields. Public constants name every log field from owner through TLS and tail. `LOG_ENTRY_REGEXP` concatenates named groups in AWS log order, `AWS_LOG_REGEXP_GROUPS` exposes an immutable ordered list, and `LOG_ENTRY_PATTERN` is the compiled pattern.

## State, dependencies, and integration
The class is stateless apart from static constants. It depends on Java regex and collections and Hadoop classification annotations. It is intended for diagnostics/tests that need to parse S3 logs and correlate audit referrer data.

## Risks and test signals
S3 log formats can evolve; the tail group is designed as forward-compatible catch-all. Tests should parse representative log lines with quoted user-agent/referrer values, missing fields represented as `-`, unexpected tails, and group-order assertions.
