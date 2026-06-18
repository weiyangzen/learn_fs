# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditor.java

## Purpose
`NoopAuditor` is an `OperationAuditor` implementation that creates `NoopSpan` instances and performs no audit logging or enforcement.

## Important APIs and control flow
Constructors create an unbonded no-op span and optionally retain activation callbacks. `createSpan()` returns a new `NoopSpan` with a generated span ID and paths. `getUnbondedSpan()` returns the unbonded span. `createAndStartNoopAuditor()` builds options with an empty IO statistics store, initializes, starts, and returns a no-op auditor.

## State, dependencies, and integration
State is the unbonded span and optional callbacks. It extends `AbstractOperationAuditor`, so it still has service lifecycle, IDs, flags, and IO statistics. It is used by `NoopAuditManagerS3A` and tests.

## Risks and test signals
Even no-op spans should have valid IDs when created through the auditor. Tests should verify activation callbacks fire, unbonded span is stable, and lifecycle methods match `OperationAuditor` expectations.
