# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSUnsupportedFeatureException.java

Purpose: typed service IOException for object stores that reject a requested S3 feature.

Important APIs/types: extends `AWSServiceIOException`; overrides `retryable()` to `false`.

Control flow: exception translation creates this when a feature such as change detection or another S3 capability is unsupported. Callers should disable the feature rather than retry.

State and persistence behavior: wraps original service exception only.

Dependencies and integration points: integrates with S3A feature negotiation and compatibility paths for third-party S3-compatible stores.

Risks: accurate mapping matters; misclassifying a transient service problem as unsupported prevents useful retries.

Test signals: compatibility tests should verify unsupported-feature responses fail fast and surface actionable diagnostics.
