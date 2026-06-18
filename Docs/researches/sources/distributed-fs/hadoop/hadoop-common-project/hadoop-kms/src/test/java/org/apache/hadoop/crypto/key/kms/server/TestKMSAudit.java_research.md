# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAudit.java

## Purpose
`TestKMSAudit.java` verifies KMS audit logging behavior: aggregation, unauthenticated/unauthorized/error formats, and configured audit logger initialization.

## Important APIs, Types, and Functions
- `setUp()` captures `System.err`, loads `log4j-kmsaudit.properties`, and creates `KMSAudit`.
- `cleanUp()` restores `System.err`, resets Log4j, and shuts down `KMSAudit`.
- `FilterOut` lets the test swap the backing `ByteArrayOutputStream` after each assertion.
- `testAggregation()` checks that selected crypto operations aggregate repeated OK records while management operations remain unaggregated.
- `testAggregationUnauth()` verifies that unauthorized events evict or flush aggregation state, accepting either ordering for asynchronous invalidation.
- `testAuditLogFormat()` validates OK, UNAUTHORIZED, ERROR, and UNAUTHENTICATED log formats.
- `testInitAuditLoggers()` uses reflection to inspect `KMSAudit.auditLoggers`, verifies default `SimpleKMSAuditLogger`, duplicate suppression, and failure when a configured logger class cannot load.

## Control Flow and State
Tests drive `kmsAudit.ok()`, `unauthorized()`, `error()`, `unauthenticated()`, and `evictCacheForTesting()`, then compare captured output against regexes. Aggregation state lives inside `KMSAudit` caches until evicted or invalidated by an unauthorized event.

## Dependencies and Integration Points
The file integrates `KMSAudit`, `KMS.KMSOp`, `KMSAuditLogger`, `SimpleKMSAuditLogger`, Log4j configuration, Hadoop `UserGroupInformation`, and Apache Commons `FieldUtils`. It protects the audit contract expected by operators and downstream log processing.

## Risks and Edge Cases
The tests are regex-heavy and timing-sensitive around asynchronous cache invalidation. They strip a known deprecated config warning from output to reduce noise. Any format change in audit logs is intentionally visible as a test failure.

## Test Signals
The test suite gives direct evidence that audit aggregation preserves counts and intervals for crypto operations, unauthenticated and error events remain structured, and invalid logger configuration fails early.
