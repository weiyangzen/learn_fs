# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAudit.java

## Purpose
`KMSAudit.java` centralizes audit event creation, aggregation, logger plugin initialization, and shutdown for Hadoop KMS.

## Important APIs, Types, and Functions
`AGGREGATE_OPS_WHITELIST` identifies high-volume operations eligible for aggregation: key version/current key reads and EEK decrypt/generate/reencrypt. Public methods include `ok`, `unauthorized` for KMS and key operations, `error`, `unauthenticated`, `shutdown`, and `evictCacheForTesting`. Logger classes are loaded from `hadoop.kms.audit.logger`, defaulting to `SimpleKMSAuditLogger`.

## Control Flow
Construction reads the aggregation window, builds a Guava cache with `expireAfterWrite`, schedules periodic cleanup, and instantiates configured `KMSAuditLogger` implementations. `op` either logs immediately or aggregates by `(user, key, op)`. Unauthorized events invalidate any aggregate cache entry and are logged immediately. Expired aggregate events with positive access count are logged and reinserted to continue the aggregation window.

## State and Persistence
Runtime state consists of the aggregation cache, scheduled executor, and audit logger list. Persistence is indirect through the configured logging backend. `shutdown` stops the executor and calls each logger's cleanup.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, UGI, reflection utilities, Guava cache, and `KMSAuditLogger`. `KMS`, `KMSACLs`, `KMSAuthenticationFilter`, and `KMSExceptionsProvider` call into it for success, authorization, unauthenticated, and error events.

## Risks
Audit format compatibility is critical because downstream parsers depend on it. Aggregation changes event timing and count semantics for whitelisted operations. Logger initialization failures abort startup by throwing runtime exceptions. The remote host passed by most operation paths is `"Unknown"`, while unauthenticated and exception paths include request context.

## Test Signals
Tests should verify first-event logging, aggregation eviction and count, immediate unauthorized logging, configured logger loading and failure behavior, shutdown cleanup, and that non-whitelisted or incomplete events bypass aggregation.
