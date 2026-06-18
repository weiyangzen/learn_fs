# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PutTracker.java

## Purpose
Base callback object attached to multipart output streams. The default implementation represents ordinary uploads where final multipart completion happens when the stream closes and output is immediately visible.

## Important APIs, Types, And Functions
`initialize()` returns whether MPU should start immediately; default false. `outputImmediatelyVisible()` defaults true. `aboutToComplete(uploadId, parts, bytesWritten, iostatistics)` defaults true, telling the stream to complete the MPU. `getDestKey()` returns the S3 key used by PUT/MPU operations.

## Control Flow
An output stream creates or receives a tracker, calls `initialize()` before upload setup, writes parts, then calls `aboutToComplete()` near close. Subclasses such as `MagicCommitTracker` override these hooks to delay final visibility and write commit metadata instead of completing the MPU.

## State And Persistence
Only stores `destKey`. It does not persist commit metadata or track upload parts itself.

## Dependencies And Integration Points
Integrated with S3A write streams and magic committer subclasses; consumes AWS SDK `CompletedPart` lists and optional `IOStatistics`.

## Risks
The default behavior is intentionally permissive. Any delayed-commit implementation must override both visibility and completion behavior consistently or files may become visible too early.

## Test Signals
Verify default trackers cause normal MPU completion, expose the original key, and report immediate visibility. Subclass tests should assert overridden return values drive stream close behavior.
