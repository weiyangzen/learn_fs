# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/MemoryHungryAuditor.java

## Purpose

`MemoryHungryAuditor.java` is a deliberately large test auditor used to expose memory leaks in active audit-manager thread/span tracking.

## Important APIs, Types, and Functions

It extends `AbstractOperationAuditor`, publishes class name `NAME`, allocates `MANAGER_SIZE` bytes per auditor and `SPAN_SIZE` bytes per span, counts instances and spans, overrides `createSpan()`, `getUnbondedSpan()`, and `noteSpanReferenceLost()`, and defines nested `MemorySpan`.

## Control Flow

Each created span increments `spanCount` and returns a new `MemorySpan`. `getUnbondedSpan()` lazily creates one unbonded span. `MemorySpan.activate()` returns itself and `deactivate()` is intentionally empty, leaving manager-side map behavior as the test focus.

## State and Persistence Behavior

State is intentionally memory-heavy: per-auditor byte array, per-span byte array, static instance counter, instance span counter, and cached unbonded span.

## Dependencies and Integration Points

It integrates with `ActiveAuditManagerS3A` leak tests and the `AbstractAuditSpanImpl` contract.

## Risks and Edge Cases

Because it consumes tens of MB across many managers, test parameters must remain bounded. It is not suitable for general audit tests or production use.

## Test Signals

Signals are heap pressure, instance/span counts, and whether weak-reference pruning frees manager/span references before out-of-memory conditions.
