# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedMultipartUploaderException.java

## Purpose
Checked IOException indicating multipart upload is unavailable for a filesystem or path.

## Important APIs, Types, and Functions
Single message constructor; public stable type.

## Control Flow
No internal flow; callers throw when MultipartUploaderBuilder or filesystem capability paths cannot satisfy the request.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Integrated with MultipartUploader, MultipartUploaderBuilder, and filesystem capability code.

## Risks and Test Signals
Tests should assert unsupported stores fail with this type rather than generic IOException or UnsupportedOperationException.
