# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditor.java

## Purpose
`OperationAuditor` is the plugin interface for S3A audit services that create spans, expose IO statistics, and optionally enforce access checks.

## Important APIs and control flow
It extends `Service`, `IOStatisticsSource`, and `AuditSpanSource<AuditSpanS3A>`. Implementors initialize from `OperationAuditorOptions`, receive updated `AuditorFlags`, provide an unbonded span, produce an auditor ID, and may override `checkAccess()` and `noteSpanReferenceLost()`. The default access check permits access.

## State, dependencies, and integration
Implementations usually hold configuration, IO statistics, flags, span ID sources, and unbonded span state. It integrates through `AuditIntegration.createAndInitAuditor()` and `ActiveAuditManagerS3A`.

## Risks and test signals
Third-party auditors can affect filesystem operations if callbacks throw. Tests should cover lifecycle order, access-check behavior, IO statistics availability, and weak-reference span-loss notification.
