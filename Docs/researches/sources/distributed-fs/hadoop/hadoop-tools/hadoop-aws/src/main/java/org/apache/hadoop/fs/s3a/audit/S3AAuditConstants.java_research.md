# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3AAuditConstants.java

## Purpose
`S3AAuditConstants` centralizes public/limited-private configuration keys and symbolic names for S3A auditing.

## Important APIs and control flow
Constants include `AUDIT_ENABLED`, default enabled state, audit service class key and default class names, deprecated v1 request handler key, v2 execution interceptor key, reject-out-of-span key, referrer header enable/filter keys, `INITIALIZE_SPAN`, `OUTSIDE_SPAN`, and the `UNAUDITED_OPERATION` log marker.

## State, dependencies, and integration
The class is a static constant holder with a private constructor. It is consumed by `AuditIntegration`, `ActiveAuditManagerS3A`, `LoggingAuditor`, and configuration docs/tests.

## Risks and test signals
Configuration-key changes are user-visible. Tests should validate defaults, deprecated handler warnings, referrer filtering, and reject-out-of-span behavior driven by these keys.
