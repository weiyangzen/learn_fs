# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditSpanLifecycle.java

## Purpose

`TestAuditSpanLifecycle.java` verifies basic audit span lifecycle semantics for the no-op audit manager path created through the shared auditing test base.

## Important APIs, Types, and Functions

The class extends `AbstractAuditingTest`, uses `noopAuditConfig()`, captures the initial reset span in `setup()`, and tests `createSpan()`, `activate()`, `close()`, `deactivate()` semantics through the `AuditSpan` interface.

## Control Flow

Tests create one or more spans, assert the latest span becomes active, reactivate earlier spans, close active and inactive spans, and confirm the reset/unbonded span is restored where expected.

## State and Persistence Behavior

Span state is thread-bound through the manager. The initial reset span is invalid and should remain active when no valid span is bound.

## Dependencies and Integration Points

This validates `AuditManagerS3A` span management, `AuditSpan` validity, execution interceptor creation, and manager stop behavior.

## Risks and Edge Cases

Incorrect deactivation could leave stale spans active or allow the reset span to be closed. The tests specifically guard inactive-span close and reset-span close behavior.

## Test Signals

Signals are active span object identity, validity predicates, non-empty interceptor lists, and successful manager stop.
