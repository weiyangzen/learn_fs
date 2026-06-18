# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/package-info.java

## Purpose
This package descriptor documents S3A auditing and tracing support as an extension-facing but unstable API.

## Important APIs and control flow
It states that audit services are instantiated during S3A filesystem initialization, selected by `S3AAuditConstants.AUDIT_SERVICE_CLASSNAME`, and must implement `OperationAuditor` to provide audit spans for public filesystem calls and related operations.

## State, dependencies, and integration
No runtime state exists. The package depends on Hadoop classification annotations and documents integration with `AuditSpan`, `OperationAuditor`, and S3A configuration.

## Risks and test signals
The package explicitly warns of instability as audit/tracing evolves. Extension compatibility tests should instantiate configured auditors and validate lifecycle and span creation rather than relying on implementation packages.
