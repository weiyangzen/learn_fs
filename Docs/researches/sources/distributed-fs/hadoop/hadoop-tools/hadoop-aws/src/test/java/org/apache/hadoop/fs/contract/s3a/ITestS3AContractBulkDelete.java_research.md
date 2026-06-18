# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractBulkDelete.java

Purpose: S3A implementation of the Hadoop bulk-delete contract, validating both multi-object delete and single-delete fallback behavior.

Important APIs/types/functions: extends `AbstractContractBulkDeleteTest`, parameterized by `enableMultiObjectDelete`. `createConfiguration()` disables FS caching, propagates bucket options, sets `BULK_DELETE_PAGE_SIZE=20`, and toggles `ENABLE_MULTI_DELETE`. Overrides `getExpectedPageSize()` and `validatePageSize()`. Adds tests for zero page-size preconditions, disabled multi-delete page size, directory inputs, parent directories, and rate limiting.

Control flow: tests create paths under contract `basePath`, call wrapped `bulkDelete_delete()`, and assert S3A-specific directory markers remain directories. Rate-limit test creates 20 files, deletes repeatedly, and checks `STORE_IO_RATE_LIMITED_DURATION.mean` grows after repeated calls.

State and persistence: mutates bucket objects during tests; uses fresh uncached filesystems for some configuration variants.

Dependencies and integration: integrates `BulkDelete`, S3A constants, `S3AUtils.propagateBucketOptions`, wrapped IO bulk-delete APIs, and store IOStatistics.

Risks: expected directory retention is S3A-specific and differs from real hierarchical filesystems. Rate-limit assertions depend on configured throttling and repeated operations. Disabled multi-delete mode must keep page size at 1.

Test signals: integration and parameterized coverage for page-size validation, directory non-deletion semantics, and rate-limit metrics.
