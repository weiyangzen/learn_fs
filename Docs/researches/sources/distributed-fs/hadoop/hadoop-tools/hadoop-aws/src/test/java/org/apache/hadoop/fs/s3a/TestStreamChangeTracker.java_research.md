# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestStreamChangeTracker.java

## Purpose

`TestStreamChangeTracker.java` verifies `ChangeTracker`, the S3A component that detects object changes during stream reads and copy operations using ETag or VersionId constraints.

## Important APIs, Types, and Functions

Tests create policies through `ChangeDetectionPolicy.createPolicy(mode, source, requireVersion)` and instantiate `ChangeTracker` with `CountingChangeTracker` and `S3ObjectAttributes`. The suite exercises `maybeApplyConstraint()` on `GetObjectRequest.Builder` and `CopyObjectRequest.Builder`, `processResponse()` for GET and COPY responses, and `processException()` for S3 precondition failures.

## Control Flow

Client-mode tests observe first response revision IDs, then feed mismatching responses and expect `RemoteFileChangedException`. Server-mode tests verify request constraints are applied after a revision is known and that null/precondition failure responses are treated as server-reported changes. Required-version tests expect `NoVersionAttributeException` when the selected revision source is missing.

## State and Persistence Behavior

The tracker retains a current revision ID and mismatch count in memory. `CountingChangeTracker` records mismatch events for statistics. No external state is persisted.

## Dependencies and Integration Points

The suite covers AWS SDK v2 S3 GET/COPY models, S3A `S3ObjectAttributes`, Hadoop `PathIOException`, `RemoteFileChangedException`, and HTTP 412 precondition translation.

## Risks and Edge Cases

Risks include silent stale reads when constraints are not applied, over-strict behavior against endpoints without version IDs, and missed copy failures due to SDK exception shape. Warning mode is intentionally one-shot to avoid repeated mismatch noise.

## Test Signals

Signals are applied-constraint booleans, stored revision IDs, exact mismatch counts, and expected exceptions for version absence, revision mismatch, and 412 precondition failure.
