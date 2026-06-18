# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/UnsupportedRequestException.java

## Purpose
`UnsupportedRequestException` is a Hadoop `PathIOException` subclass used when S3A or its audit layer rejects an operation as unsupported for a specific path.

## Important APIs and control flow
It provides constructors for path plus cause, path plus error text, and path plus error text plus cause. There is no additional behavior.

## State, dependencies, and integration
The exception stores state inherited from `PathIOException`. It is used by `AuditIntegration.translateAuditException()` for `AuditOperationRejectedException` and may be used by request factory implementations.

## Risks and test signals
Tests should verify translated audit rejections preserve path, message, and cause. Since retry policy may treat exception types specially, changing its superclass would be a compatibility risk.
