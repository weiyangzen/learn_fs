# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/MultipartUploadCleaner.java

## Purpose
`MultipartUploadCleaner` lazily schedules automatic abortion of S3 multipart uploads after a configured timeout. Instead of scanning the filesystem, it tracks known upload IDs and deletes their temporary part directory and metadata file when expired.

## Important APIs, Types, and Functions
The singleton API includes `getInstance`, `shutdown`, static `apply`, static `cancelAbort`, `tryAbortMultipartUpload`, and `getRetryDelay`. Internal helpers include `apply(AbortTask,long)`, `removeTaskRecord`, `containsTaskRecord`, and `canRetry`. Nested `AbortTask` implements `Runnable` and defines equality/hash by bucket, object, and upload ID.

## Control Flow, State, and Persistence
The singleton is lazily initialized with timeout, retry count, retry delay, scheduled-pool size, and a `ConcurrentHashMap<AbortTask,ScheduledFuture<?>>`. `apply` schedules an abort task immediately and records its future. `tryAbortMultipartUpload` computes the multipart temp directory, checks upload metadata/status, returns a positive delay if the upload has not expired, otherwise deletes the user temp directory recursively and deletes the metadata file from the meta filesystem. Missing files mean the upload was already completed or aborted and no retry is needed. `AbortTask.run` reschedules itself for the returned delay, removes itself after success/no-retry, or retries after I/O/Alluxio failures until the configured count is exceeded.

## Dependencies and Integration Points
It integrates S3 multipart initiate/upload/complete/abort paths with Alluxio `FileSystem`, S3 temp-path utilities, upload ID metadata files, Java scheduled executors, and proxy configuration keys. `CompleteMultipartUploadHandler` cancels cleaner tasks after successful completion.

## Risks
`apply` overwrites existing task records after scheduling a new future, so duplicate scheduling can leave an older future not cancelled. `shutdown` stops the executor but does not clear `mTasks` before nulling the singleton. Error logging swaps bucket/object argument order in one message. Retry exhaustion leaves task records unless the final failure path removes them. Equality ignores filesystem instances, so same bucket/object/upload ID across different FS contexts collides intentionally or accidentally.

## Test Signals
Important tests include scheduling and cancellation, duplicate apply behavior, not-yet-expired rescheduling, expired upload deletion, already-missing upload handling, retry and retry exhaustion, singleton shutdown/recreation, and integration with successful complete-multipart cleanup.
