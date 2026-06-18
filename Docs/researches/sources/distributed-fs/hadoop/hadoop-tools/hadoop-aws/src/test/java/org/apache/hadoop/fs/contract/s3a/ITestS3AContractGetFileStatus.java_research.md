# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractGetFileStatus.java

Purpose: S3A binding for get-file-status contract tests, tuned to exercise multipage listings.

Important APIs/types/functions: extends `AbstractContractGetFileStatusTest`. `createConfiguration()` disables FS caching and sets `MAX_PAGING_KEYS=2`. `teardown()` logs filesystem details before superclass cleanup. Timeout returns `S3A_TEST_TIMEOUT`.

Control flow: inherited tests trigger status lookups under constrained list pagination so directory probes cover multi-page behavior.

State and persistence: inherited status tests create files/directories; test configuration uses uncached filesystems.

Dependencies and integration: S3A paging constants, S3A test utilities, and contract status suite.

Risks: low page size increases request count and can amplify failures under fault injection; timeout is extended accordingly.

Test signals: integration coverage for status resolution across paginated S3 listings.
