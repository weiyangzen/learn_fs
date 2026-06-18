# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/files/TestUploadEtag.java

## Purpose
Unit tests for conversion between AWS SDK `CompletedPart` and Hadoop `UploadEtag`, including optional per-part checksum metadata.

## Important APIs, Types, and Functions
The suite targets `UploadEtag.fromCompletedPart(CompletedPart)` and `UploadEtag.toCompletedPart(UploadEtag, int)`. It covers checksum algorithms `CRC32`, `CRC32C`, `SHA1`, `SHA256`, and the no-checksum case.

## Control Flow and Behavior
Each `fromCompletedPart` test builds a SDK `CompletedPart` with an ETag and exactly one checksum field, then verifies the resulting `UploadEtag` has the right ETag, algorithm string, and checksum value. Each `toCompletedPart` test creates an `UploadEtag` and asserts the corresponding SDK checksum getter is populated or null.

## State, Persistence, and Dependencies
There is no persistence. Dependencies are AWS SDK v2 S3 model classes and AssertJ.

## Integration Points, Risks, and Test Signals
The conversion is used when serializing pending multipart commit data and later completing an MPU. This test protects checksum preservation across pending commit files; a regression could cause complete-MPU requests to omit required checksum metadata for checksum-enabled uploads.
