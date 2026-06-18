# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/ValidationFailure.java

## Purpose
Checked validation exception used by persisted commit data loaders and serializers. It is an `IOException` so invalid commit metadata flows through existing IO failure paths.

## Important APIs, Types, And Functions
`ValidationFailure(String, Object...)` formats messages. Static `verify(boolean, String, Object...)` throws `ValidationFailure` when a precondition is false.

## Control Flow
Persistent data classes call `verify()` during `validate()` and Java deserialization hooks. Failures abort loading, committing, or saving pending commit metadata.

## State And Persistence
No extra state beyond the formatted exception message.

## Dependencies And Integration Points
Used heavily by `SinglePendingCommit`, `PendingSet`, and `SuccessData`; those classes surface validation problems as IO failures to commit protocols.

## Risks
Validation messages use `String.format()`, so invalid format strings in callers would mask the original validation intent.

## Test Signals
Validate success/failure branches and ensure bad persistent data yields `ValidationFailure` rather than unchecked exceptions.
