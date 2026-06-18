<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObject.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObject.java

Purpose: encapsulates low-level S3 range GET behavior for prefetch streams, including request construction, change tracking, statistics, and stream draining on close.

Important APIs/types/functions: constructor validates read context, attributes, callbacks, statistics, and `ChangeTracker`. `getReadInvoker()`, `getStatistics()`, `getPath()`, static `getPath(S3ObjectAttributes)`, and `size()` expose metadata. `openForRead(long,int)` validates range, increments stream-open stats, builds a ranged `GetObjectRequest`, applies change constraints, tracks get duration, invokes `client.getObject()`, and processes response change metadata. Package-private `close(ResponseInputStream,int)` drains synchronously below async drain threshold or submits `SDKStreamDrainer`.

Control flow: `S3ARemoteObjectReader` opens a ranged stream, reads bytes, then calls `close()` with remaining bytes so the SDK stream is drained or aborted appropriately.

State/persistence: holds immutable references to context, attributes, callbacks, statistics, change tracker, and derived URI. No persistence.

Dependencies/integration: AWS SDK v2 `GetObjectRequest/ResponseInputStream`, S3A `Invoker`, `S3AUtils.formatRange`, `SDKStreamDrainer`, change tracking, and stream statistics.

Risks/test signals: off-by-one range formatting, change constraint failures, and drain threshold behavior are critical. Tests should cover invalid ranges, request mutation, change tracker response handling, get duration failure tracking, and async drain submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObject.java -->
