# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractMultipartUploader.java

## Purpose
Base class for MultipartUploader implementations with shared argument validation.

## Important APIs, Types, and Functions
close(), getBasePath(), checkPath(), checkUploadId(), checkPartHandles(), checkPutArguments(), abortUploadsUnderPath().

## Control Flow
checkPath requires target string to start with base path string. checkPartHandles rejects empty maps and non-positive part indexes. abortUploadsUnderPath returns a completed future with -1 after path validation.

## State and Persistence Behavior
Stores immutable basePath only. Subclasses own upload state.

## Dependencies and Integration Points
Used by FileSystemMultipartUploader and other multipart uploader implementations.

## Risks and Test Signals
Risks are string-prefix path validation accepting sibling prefixes and default abortUploadsUnderPath sentinel behavior. Tests should validate path boundaries and argument failures.
