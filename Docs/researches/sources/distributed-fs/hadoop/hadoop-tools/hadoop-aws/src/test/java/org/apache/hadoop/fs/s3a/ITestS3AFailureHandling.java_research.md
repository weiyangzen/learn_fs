# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFailureHandling.java

Purpose: Integration tests for S3A failure handling, primarily multi-object delete behavior, paging, missing keys, and access-denied exception translation.

Important APIs/types/functions: `S3AFileSystem.removeKeys()`, AWS SDK `ObjectIdentifier` and `S3Error`, `MultiObjectDeleteException`, `StoreStatisticNames.OBJECT_BULK_DELETE_REQUEST`, `PublicDatasetTestUtils.requireDefaultExternalData()`, `RemoteIterators.toList()`, and `mappingRemoteIterator()`.

Control flow: configuration disables FS caching and enables multi-delete. Tests remove missing keys, create many files and delete them through batched bulk delete while checking request counters, delete a mix of existing/missing keys, and attempt to delete external read-only/public data to verify `MultiObjectDeleteException` and single-delete `AccessDeniedException` translation.

State and persistence: creates up to 1005 S3 objects for paging when bulk delete is enabled; external-data tests operate on configured public/read-only objects. Audit spans wrap low-level delete calls.

Dependencies and integration points: S3 multi-delete API, S3A bulk delete paging, IOStatistics counters, public external data configuration, and exception translation.

Risks: external data configuration affects endpoint overrides; bulk delete enabled/disabled changes expected request count; access-denied behavior depends on public dataset permissions; large object count makes test cost/time higher.

Test signals: catches regressions in missing-key tolerance, delete paging, bulk-delete metrics, and AWS-to-Hadoop exception mapping.
