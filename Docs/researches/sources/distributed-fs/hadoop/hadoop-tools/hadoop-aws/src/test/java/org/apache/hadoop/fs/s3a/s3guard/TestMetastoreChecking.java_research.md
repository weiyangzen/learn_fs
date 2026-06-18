# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestMetastoreChecking.java

Purpose: unit tests for deprecated S3Guard metastore configuration validation through `S3Guard.checkNoS3Guard`.

Important APIs/types/functions: `TestMetastoreChecking` extends `AbstractHadoopTestBase`; it builds a URI for `s3a://bucket/`, creates minimal `Configuration(false)` instances with `S3_METADATA_STORE_IMPL`, and checks constants `NULL_METADATA_STORE`, `S3GUARD_METASTORE_LOCAL`, and `S3GUARD_METASTORE_DYNAMO`.

Control flow: setup initializes the test filesystem URI. `chooseStore` optionally sets the configured metastore class. Tests assert no class returns false, null/local stores return true, DynamoDB store raises `PathIOException`, and unknown class raises `PathIOException` containing the class name.

State and persistence: no external store is contacted; only configuration keys and URI are used.

Dependencies/integration: S3Guard compatibility checks, Hadoop `PathIOException`, AssertJ assertions, and LambdaTestUtils.

Risks: because the code is marked deprecated, behavior is compatibility-focused; adding/removing accepted metastore names requires test updates.

Test signals: boolean outcomes for allowed/missing stores and exact exception behavior for forbidden/unknown stores.
