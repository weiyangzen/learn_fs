# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AChecksum.java

Purpose: parameterized S3 checksum-generation/validation integration tests.

Important APIs/types/functions: extends `AbstractS3ATestBase`, parameterized for `SHA256`, `CRC32C`, `SHA1`, and `UNKNOWN_TO_SDK_VERSION`. `createConfiguration()` removes checksum/audit overrides, disables FS caching, sets `CHECKSUM_ALGORITHM`, enables `CHECKSUM_VALIDATION`, and derives SDK checksum algorithm. `assertChecksum()` issues a `HeadObject` with `ChecksumMode.ENABLED` and asserts algorithm-specific checksum fields.

Control flow: `testChecksum()` writes and reads files of several sizes, then checks object metadata checksum fields. Unknown algorithm expects checksum fields like SHA256 to be null.

State and persistence: writes S3 objects under method paths and reads HEAD metadata.

Dependencies and integration: AWS SDK checksum APIs, S3A checksum support, S3A request factory, bucket option propagation, and audit option.

Risks: requires IAM permission for checksum-enabled HEAD and store support for configured algorithms. `SIZES` includes `2 ^ 12 - 1`, a bitwise XOR expression rather than exponentiation.

Test signals: parameterized integration coverage for checksum generation and metadata visibility.
