# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuditLogger.java

## Purpose
`KMSAuditLogger.java` defines the private extension interface for KMS audit loggers and the immutable-per-event data object passed to them.

## Important APIs, Types, and Functions
`OpStatus` enumerates `OK`, `UNAUTHORIZED`, `UNAUTHENTICATED`, and `ERROR`. Nested `AuditEvent` records operation object, key name, user, impersonator, remote host, extra message, start and end times, and an `AtomicLong` access count for aggregate events. Implementations must provide `initialize`, `logAuditEvent`, and `cleanup`.

## Control Flow
`AuditEvent` construction derives user and impersonator from `UserGroupInformation`, detecting proxy authentication through `AuthenticationMethod.PROXY`. `KMSAudit` mutates only the event end time and access count before dispatching to logger implementations.

## State and Persistence
The interface has no static state. `AuditEvent` carries event-local state and aggregate counters. Persistence is delegated entirely to implementations.

## Dependencies and Integration Points
It is consumed by `KMSAudit` and implemented by `SimpleKMSAuditLogger` or configured custom classes. The warning in the source documents that audit log format must remain backward-compatible.

## Risks
Because the event accepts `Object op`, loggers must handle both `KMS.KMSOp` and `KeyAuthorizationKeyProvider.KeyOpType` values, plus null for some error paths. Changing event string format or field semantics can break external audit consumers.

## Test Signals
Tests should cover proxy-user impersonator extraction, null UGI handling, access count initialization at `-1`, end-time mutation, and compatibility of custom logger invocation.
