# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PathCommitException.java

## Purpose
Small commit-specific exception type for path-scoped failures in S3A commit protocols. It keeps failures compatible with Hadoop `PathIOException` while giving committer code a clearer domain exception.

## Important APIs, Types, And Functions
`PathCommitException` extends `PathIOException` and offers constructors for string paths, `Path` instances, message-only errors, causes, and wrapped message-plus-cause failures.

## Control Flow
Committer code throws this when factory selection, destination conflict handling, validation wrapping, or commit operation conversion needs an `IOException` carrying the affected path.

## State And Persistence
No persistent state beyond the path, message, and cause stored by the superclass.

## Dependencies And Integration Points
Used by `S3ACommitterFactory`, staging committers, and `CommitOperations.makeIOE()` to normalize unexpected exceptions into Hadoop IO exceptions.

## Risks
Path may be empty when constructed from a null `Path`, so diagnostics depend on callers passing meaningful origin paths.

## Test Signals
Check message/path formatting for string and `Path` constructors and verify wrapped causes survive through `IOException` handling paths.
