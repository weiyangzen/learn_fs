# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextCreateMkdirCreatePerf.java

## Purpose
Variant of the S3A FileContext create/mkdir contract tests with mkdir create-performance mode enabled.

## Important APIs, Types, and Functions
The class extends `FileContextCreateMkdirBaseTest`, uses `S3ATestUtils.setPerformanceFlags(new Configuration(), "mkdir")`, and overrides `testMkdirRecursiveWithExistingFile()`.

## Control Flow and Behavior
Setup creates an S3A test FileContext with mkdir performance flags and delegates to inherited setup. Most tests are inherited. The overridden existing-file mkdir test expects the base test to fail with `AssertionError` containing `MKDIR_FILE_PRESENT_ERROR`, documenting that performance mode skips parent status checks and can therefore create dirs without detecting a parent file in the usual way.

## State, Persistence, and Dependencies
State is inherited FileContext test output under the S3A test path. Dependencies include S3A performance flags, base FileContext mkdir tests, and `LambdaTestUtils.intercept()`.

## Integration Points, Risks, and Test Signals
This is a focused signal for the behavioral tradeoff of mkdir performance mode. It makes the altered semantics explicit so future changes do not silently reintroduce status checks or change expected failure shape.
