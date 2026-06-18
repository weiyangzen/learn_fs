# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/audit/AuditContext.java

## Purpose
`AuditContext` is the lifecycle contract for audit-log event state.

## Important APIs, Types, And Functions
It extends `Closeable` and requires fluent `setAllowed`, `setSucceeded`, and `close`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations collect per-operation audit state, update authorization and success flags, then usually emit or enqueue on close. The interface has no direct persistence; log persistence depends on writer implementations and logging configuration. Dependencies are only Java `Closeable`. Risks include close being called before success/allowed flags are finalized, fluent setters hiding mutable state, and callers forgetting try-with-resources. Tests should target concrete contexts for string formatting, close idempotency, failure paths, and integration with async audit writer.
