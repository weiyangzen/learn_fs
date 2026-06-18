# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADelayedFNF.java

Purpose: Exercises the case where a file is successfully opened but deleted before the first read, so the failure appears lazily from the stream. It checks S3A translates that delayed object-missing condition into `FileNotFoundException`.

Important APIs/types/functions: `FSDataInputStream`, `ChangeDetectionPolicy`, `Source.VersionId`, `ContractTestUtils.createFile()`, `assertDeleted()`, and `LambdaTestUtils.intercept()`. Configuration lowers retry limits and removes change-detection overrides.

Control flow: create a small object, open it, delete it, then call `read()` and expect `FileNotFoundException`. The test assumes out when object versioning/change detection by version ID means the old opened object can still be resolved.

State and persistence: writes and deletes one S3 object. Retry settings are shortened for fast failure.

Dependencies and integration points: S3A input stream lazy GET behavior, change detection policy, retry policy, and exception translation.

Risks: bucket versioning changes semantics; retry settings affect latency and observed exception timing; prefetch or stream implementation changes may move failure earlier.

Test signals: catches regressions where delayed missing-object reads return EOF, AWS exceptions, or retry excessively instead of a Hadoop `FileNotFoundException`.
