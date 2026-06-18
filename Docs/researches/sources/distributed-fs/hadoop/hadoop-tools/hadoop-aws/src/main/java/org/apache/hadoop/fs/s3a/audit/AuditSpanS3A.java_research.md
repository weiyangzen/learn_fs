# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditSpanS3A.java

## Purpose
`AuditSpanS3A` is the S3A-specific audit span interface, combining generic Hadoop `AuditSpan` lifecycle with AWS SDK audit callbacks.

## Important APIs and control flow
It declares no new methods, but implementors inherit span activation/deactivation and all `AWSAuditEventCallbacks`/`ExecutionInterceptor` hooks.

## State, dependencies, and integration
Implementing classes carry span identifiers, operation names, timestamps, referrer state, or delegate spans. It is the common type used by audit managers, request factory callbacks, execution attributes, and active-thread span sources.

## Risks and test signals
Because the interface conflates span lifecycle and AWS callbacks, implementations must be cheap and safe during SDK execution. Tests should cover activation/deactivation validity and no-op/default behavior for unused interceptor methods.
