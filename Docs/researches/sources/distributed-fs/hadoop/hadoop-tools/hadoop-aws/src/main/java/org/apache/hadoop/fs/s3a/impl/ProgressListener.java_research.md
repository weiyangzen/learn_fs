# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListener.java

## Purpose
`ProgressListener` is a minimal callback interface for upload/progress notifications in S3A implementation code.

## Important APIs and Types
It has one default method: `progressChanged(ProgressListenerEvent eventType, long bytesTransferred)`. The default implementation is a no-op, making listener attachment optional.

## Control Flow
Upload code can call `progressChanged()` with a typed event and byte count without checking for special behavior. Implementations override the method to update counters, notify clients, or assert behavior in tests.

## State and Persistence
The interface has no fields and no persistence. State effects are entirely in implementations.

## Dependencies and Integration Points
It depends only on `ProgressListenerEvent`. It integrates with block output streams and transfer progress plumbing where progress and lifecycle events need to be observed.

## Risks and Edge Cases
Because the default method ignores all events, missing overrides silently drop progress. Implementations must tolerate frequent byte-transfer events and terminal events with zero or irrelevant byte counts.

## Test Signals
Tests should verify event propagation in upload paths and confirm no listener behavior does not affect upload success.
