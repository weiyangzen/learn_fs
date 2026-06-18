# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UploadHandle.java

## Purpose
Opaque serializable handle for multipart upload IDs.

## Important APIs, Types, and Functions
bytes() returns a ByteBuffer view; default toByteArray() copies remaining bytes; equals(Object) is part of the contract.

## Control Flow
toByteArray obtains bytes(), allocates an array sized to remaining(), and consumes that returned buffer view with get().

## State and Persistence Behavior
State lives in implementations such as BBUploadHandle. Callers must treat the handle as opaque and serializable.

## Dependencies and Integration Points
Used by MultipartUploader startUpload/putPart/complete/abort and FileSystemMultipartUploader.

## Risks and Test Signals
Risk is mutable ByteBuffer position or backing array leakage. Tests should verify repeat toByteArray behavior for implementations and equality consistency.
