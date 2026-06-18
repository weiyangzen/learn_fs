# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdir.java

Purpose: S3A binding for generic mkdir contract tests in non-performance mode.

Important APIs/types/functions: extends `AbstractContractMkdirTest`; `createConfiguration()` calls `setPerformanceFlags(super.createConfiguration(), "")`; `createContract()` returns `S3AContract`.

Control flow: all test cases are inherited.

State and persistence: inherited tests create and delete directory marker objects.

Dependencies and integration: S3A contract and performance-flag utility.

Risks: no local S3A overrides; S3-specific mkdir edge cases are handled separately in the create-performance variant.

Test signals: integration coverage for standard mkdir semantics.
