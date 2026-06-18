# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditManagerS3A.java

## Purpose
`NoopAuditManagerS3A` is the no-op audit manager used before active audit setup, when auditing is disabled, or in tests.

## Important APIs and control flow
It implements `AuditManagerS3A` and `NoopSpan.SpanActivationCallbacks`. Initialization creates a child `NoopAuditor` with an empty IO statistics store. `getActiveAuditSpan()` returns `NoopSpan.INSTANCE`. `createSpan()` returns a no-op span. `createExecutionInterceptors()` returns an empty list and `createTransferListener()` returns an empty listener. `checkAccess()` delegates to the no-op auditor. Activation callback methods are no-ops except deactivation reactivates the unbonded span.

## State, dependencies, and integration
State includes a static started `NoopAuditor`, an instance auditor reference, and a UUID ID. It integrates wherever an `AuditManagerS3A` is required without adding SDK interceptors.

## Risks and test signals
One subtlety is `getAuditor()` returns the static auditor while `serviceInit()` adds a new child auditor, so tests should verify expected lifecycle and identity. Disabled auditing tests should assert no execution interceptors are installed and operations still get harmless spans.
