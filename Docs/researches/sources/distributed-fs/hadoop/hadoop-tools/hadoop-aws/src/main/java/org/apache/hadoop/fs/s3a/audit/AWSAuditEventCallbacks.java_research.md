# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSAuditEventCallbacks.java

## Purpose
`AWSAuditEventCallbacks` extends AWS SDK v2 `ExecutionInterceptor` with S3A audit-span identity and request-creation callbacks.

## Important APIs and control flow
Implementors provide `getSpanId()` and `getOperationName()`. The default `requestCreated(SdkRequest.Builder)` hook is invoked by `RequestFactoryImpl` after S3A creates a request; AWS-created requests do not trigger it. All `ExecutionInterceptor` lifecycle methods remain available through inheritance.

## State, dependencies, and integration
The interface has no state. It depends on AWS SDK `SdkRequest` and `ExecutionInterceptor`. It is implemented by audit managers and spans, allowing both manager-level dispatch and span-specific request annotation.

## Risks and test signals
Callbacks run inside request construction or SDK execution, so exceptions can affect IO paths. Tests should verify interrupts are preserved by implementations, request-created hooks do not perform remote work, and span IDs are non-empty and unique enough for correlation.
