# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractContentSummary.java

Purpose: S3A content-summary contract coverage with an extra S3 object-store directory-count assertion.

Important APIs/types/functions: extends `AbstractContractContentSummaryTest`; overrides `createContract()` and `getFileSystem()` to return `S3AContract`/`S3AFileSystem`. `testGetContentSummaryDir()` constructs nested directories and one file, then asserts summary directory/file counts.

Control flow: creates `a`, `a/b`, `a/b/a`, and `d/e/f`; touches `a/b/file`; calls `fs.getContentSummary(baseDir)` and expects 7 directories and 1 file.

State and persistence: writes directories and one marker/file under the method path.

Dependencies and integration: uses `S3AFileSystem.getContentSummary`, Hadoop `ContentSummary`, AssertJ, and `ContractTestUtils.touch`.

Risks: directory counts depend on how S3A synthesizes directories and marker objects from listings.

Test signals: integration coverage for content-summary traversal over explicit and implicit directory objects.
