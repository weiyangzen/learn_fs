# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/S3AInternalAuditConstants.java

## Purpose
`S3AInternalAuditConstants` defines internal-only audit constants.

## Important APIs and control flow
The key constant is `AUDIT_SPAN_EXECUTION_ATTRIBUTE`, an AWS SDK `ExecutionAttribute<AuditSpanS3A>` used to attach a span to one request/response execution.

## State, dependencies, and integration
The class is a static holder. It depends on AWS SDK `ExecutionAttribute` and `AuditSpanS3A`. It is used by `AuditIntegration` and `ActiveAuditManagerS3A`.

## Risks and test signals
This attribute name is the cross-callback binding key. Tests should verify round-trip attachment and that external code does not rely on the internal constant as a stable public API.
