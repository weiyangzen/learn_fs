# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RemoteFileChangedException.java

Purpose: path exception for detecting that an S3 object changed or disappeared relative to an expected version during operations such as reads or rename.

Important APIs/types: extends `PathIOException`; constants `PRECONDITIONS_FAILED` and `FILE_NOT_FOUND_SINGLE_ATTEMPT`; constructors accept path, operation, message, and optional cause, then call `setOperation(operation)`.

Control flow: thrown by change-detection or rename code when object metadata no longer matches expectations, such as open stream revalidation failure or file disappearance between list and copy.

State and persistence behavior: exception holds path, operation, message, and optional cause only.

Dependencies and integration points: integrates S3A change detection, conditional requests, input streams, and rename operations with Hadoop path-aware errors.

Risks: object stores are eventually/concurrently mutable; this exception marks consistency or race failures that callers may or may not retry safely depending on operation semantics.

Test signals: tests should cover version/ETag mismatch, precondition failure mapping, disappeared rename source, operation field preservation, and cause preservation.
