# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSLowLevelOutputStream.java

## Purpose
`TOSLowLevelOutputStream` is the streaming/multipart upload implementation for TOS. It extends Alluxio's `ObjectLowLevelOutputStream` and supplies TOS-specific multipart init, upload, complete, abort, and single-object upload hooks.

## APIs and Control Flow
The constructor passes bucket, key, executor, configured partition size, and UFS config to the superclass and stores the `TOSV2` client. `initMultiPartUploadInternal` calls `createMultipartUpload` and stores the upload ID. `uploadPartInternal` wraps a file input stream with `TosRepeatableBoundedFileInputStream`, chooses the last-part size when needed, uploads a part, and records its ETag in `mTags`. `completeMultiPartUploadInternal` sends the uploaded part list and stores the completed ETag. `abortMultiPartUploadInternal`, `createEmptyObject`, and `putObject` map the remaining object-store operations.

## State, Persistence, and Dependencies
Persistent state is the target TOS object or multipart upload. Runtime state includes the TOS client, synchronized uploaded-part list, volatile upload ID, and content hash. It depends on Alluxio streaming upload infrastructure, Guava `ListeningExecutorService`, Volcengine multipart model types, and Java file I/O.

## Risks and Test Signals
`uploadPartInternal` catches `IOException` but not `TosException`, so SDK part-upload failures may propagate differently from other methods. `mTags` is synchronized but multipart completion order depends on how the superclass schedules and waits for uploads. MD5 parameters are accepted but unused. `TOSLowLevelOutputStreamTest` covers empty, small, large, and flushed writes, plus content hash selection.
