# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListenerEvent.java

## Purpose
`ProgressListenerEvent` enumerates upload and stream progress lifecycle events used by S3A progress listeners and tests.

## Important APIs and Types
Events include close, put start/completion/interruption/failure, byte transfer, multipart initiation/abort/completion, and part start/completion/success/abort/failure.

## Control Flow
Upload implementations emit these enum values through `ProgressListener.progressChanged()`. Consumers distinguish lifecycle transitions and byte-count progress by event type.

## State and Persistence
The enum is stateless and persistent only as an in-process event vocabulary.

## Dependencies and Integration Points
It integrates with S3A block output stream and progress listener implementations. It has no external dependencies.

## Risks and Edge Cases
Some event comments are imprecise or contain typos; consumers should rely on enum names. `TRANSFER_PART_COMPLETED_EVENT` explicitly does not imply success, so success/failure handling must use the more specific events where available.

## Test Signals
Tests should check that upload paths emit terminal events consistently and that multipart part completion and success/failure events are not conflated.
