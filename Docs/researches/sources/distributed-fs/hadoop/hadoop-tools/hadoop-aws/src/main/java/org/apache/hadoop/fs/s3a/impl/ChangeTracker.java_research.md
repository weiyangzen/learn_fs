<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeTracker.java

## Purpose

`ChangeTracker` tracks a single object's selected revision id while an S3A stream or copy operation progresses and enforces the configured `ChangeDetectionPolicy`.

## Important APIs, Types, and Functions

It exposes `getRevisionId()`, `getSource()`, `maybeApplyConstraint()` overloads for GET/COPY/HEAD builders, `processResponse()` for GET and COPY responses, `processException()`, and metadata processors for HEAD/GET responses.

## Control Flow

The constructor seeds `revisionId` from initial object attributes. Server-mode constraints are applied only when a revision id is known. Response processing pins the first available revision id, throws if required versions are absent, and on mismatches delegates to policy handling while incrementing mismatch statistics. HTTP 412 SDK exceptions become `RemoteFileChangedException`.

## State and Persistence Behavior

The tracker stores mutable in-memory `revisionId` plus references to policy, URI, and statistics. It is per-stream/per-operation, not persisted.

## Dependencies and Integration Points

It integrates with S3A input streams, copy flows, `ChangeTrackerStatistics`, AWS SDK responses/builders/exceptions, and `NoVersionAttributeException`.

## Risks and Edge Cases

If no initial revision is known, the first response becomes authoritative. Null GET responses with an expected revision are treated as remote changes. Copy responses cannot prove equality of source and destination revision.

## Test Signals

Cover initial revision seeding, server constraints, first-response pinning, ETag/version mismatch, warn mode counters, missing required versions, 412 exception translation, null GET responses, and copy response validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeTracker.java -->
