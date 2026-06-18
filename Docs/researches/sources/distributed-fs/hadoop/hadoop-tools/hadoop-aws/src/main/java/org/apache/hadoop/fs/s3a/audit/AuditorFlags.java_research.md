# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditorFlags.java

## Purpose
`AuditorFlags` defines dynamic flags that can be passed into audit managers and auditors.

## Important APIs and control flow
The only current value is `PermitOutOfBandOperations`, which tells auditors to allow operations outside an active span.

## State, dependencies, and integration
The enum has no state. It is consumed through `EnumSet<AuditorFlags>` by `AuditManagerS3A`, `OperationAuditor`, and `AbstractOperationAuditor`.

## Risks and test signals
Flag semantics override configuration in `AbstractOperationAuditor`. Tests should verify that setting `PermitOutOfBandOperations` disables reject-out-of-span behavior and that empty or missing flag sets do not cause null-pointer failures in auditor code.
