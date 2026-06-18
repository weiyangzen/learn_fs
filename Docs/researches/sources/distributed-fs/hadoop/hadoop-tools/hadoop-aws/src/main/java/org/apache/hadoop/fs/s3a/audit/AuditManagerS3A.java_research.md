# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditManagerS3A.java

## Purpose
`AuditManagerS3A` is the S3A service interface that binds audit spans to the AWS SDK and active thread context.

## Important APIs and control flow
The interface extends `Service`, `AuditSpanSource<AuditSpanS3A>`, `AWSAuditEventCallbacks`, and `ActiveThreadSpanSource<AuditSpanS3A>`. It exposes `getAuditor()`, `createExecutionInterceptors()`, `createTransferListener()`, `checkAccess()`, and `setAuditFlags()`. Implementations create SDK interceptors and transfer listeners that preserve audit context across AWS request execution.

## State, dependencies, and integration
No interface state exists. Dependencies include AWS SDK execution interceptors, transfer-manager progress listeners, Hadoop `Path`, `FsAction`, `S3AFileStatus`, and `AuditorFlags`. It integrates with S3A filesystem initialization, access checks, request factory callbacks, and SDK client construction.

## Risks and test signals
Incorrect interceptor ordering or transfer listener behavior can lose span context for multipart/copy operations. Tests should verify active span propagation, soft access checks, flags flowing to auditors, and mutable interceptor lists accepting configured extras.
