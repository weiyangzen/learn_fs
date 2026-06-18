# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContext.java

## Purpose
Integration test for S3A `FileContext` scheme binding through Hadoop `AbstractFileSystem`.

## Important APIs, Types, and Functions
The class extends `TestFileContext`. `testScheme()` creates a configuration mapping `fs.AbstractFileSystem.s3.impl` to `org.apache.hadoop.fs.s3a.S3A`, obtains a `FileContext` for `s3://mybucket/path`, and checks default filesystem and qualified path schemes.

## Control Flow and Behavior
The test constructs a URI using the `s3` scheme rather than `s3a`, binds the abstract filesystem implementation, then verifies both `fc.getDefaultFileSystem().getUri().getScheme()` and `fc.makeQualified(new Path("tmp/path"))` preserve `s3`.

## State, Persistence, and Dependencies
No remote IO is required by the test itself. Dependencies include `FileContext`, `TestFileContext`, Hadoop `Path`, and S3A abstract filesystem binding configuration.

## Integration Points, Risks, and Test Signals
This guards FileContext URI binding and qualification behavior for the legacy `s3` abstract scheme. A failure suggests misconfiguration in abstract filesystem implementation mapping or path qualification.
