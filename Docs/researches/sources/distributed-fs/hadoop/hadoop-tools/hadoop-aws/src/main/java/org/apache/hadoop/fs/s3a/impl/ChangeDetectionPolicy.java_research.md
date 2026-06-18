<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeDetectionPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeDetectionPolicy.java

## Purpose

`ChangeDetectionPolicy` defines how S3A detects remote object changes during reads, copies, and metadata checks.

## Important APIs, Types, and Functions

The `Source` enum selects `ETag`, `VersionId`, or `None`; `Mode` selects `Client`, `Server`, `Warn`, or `None`. Public factories are `getPolicy(Configuration)` and `createPolicy(...)`. Abstract methods extract revision ids and apply request constraints. Nested policy classes implement ETag, version-id, and no-op behavior.

## Control Flow

Configuration strings are normalized to lower case and unknown values fall back to defaults with warnings. Server mode applies `If-Match`, copy-source-if-match, or version-id constraints depending on source. `onChangeDetected()` either ignores, warns once, or returns a `RemoteFileChangedException`.

## State and Persistence Behavior

Policy instances are immutable: mode, require-version flag, and a `LogExactlyOnce` warning helper. There is no persisted state.

## Dependencies and Integration Points

It depends on AWS SDK request/response builders, `S3ObjectAttributes`, S3A change-detection constants, `RemoteFileChangedException`, and logging.

## Risks and Edge Cases

ETag can change across multipart/encrypted copies and may not be a stable content checksum. Version id requires bucket versioning. Warn mode only logs first mismatch per stream statistics count. Unknown config silently falls back after logging.

## Test Signals

Test config parsing, each source/mode pair, request constraints, missing version handling, no-op policy behavior, warn-once semantics, and exception content on client/server mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeDetectionPolicy.java -->
