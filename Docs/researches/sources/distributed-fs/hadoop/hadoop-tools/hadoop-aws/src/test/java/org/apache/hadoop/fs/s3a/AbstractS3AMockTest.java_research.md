# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractS3AMockTest.java

Purpose: base class for S3A unit tests backed by a mock AWS SDK S3 client instead of a live bucket.

Important APIs/types/functions: defines `BUCKET`, reusable `NOT_FOUND` `AwsServiceException`, protected `fs`, `s3`, and `conf`. `createConfiguration()` installs `MockS3ClientFactory`, sets multipart size/probe/region, forces blocking stream drain, and tight retry settings. `setup()` initializes `S3AFileSystem` at `s3a://mock-bucket`, unsets encryption, and captures the mock S3 client. `teardown()` closes the FS.

Control flow: each test gets a fresh configuration and filesystem; mock client is retrieved from internals with a purpose string.

State and persistence: per-test in-memory/mock filesystem state; no real S3 persistence.

Dependencies and integration: AWS SDK `S3Client`, Hadoop `S3ClientFactory`, mock factory, S3A internals, and retry/multipart constants.

Risks: tests inheriting this base must account for mock behavior differing from real S3. Encryption is explicitly unset to avoid path IO errors.

Test signals: foundational setup for mock-based S3A tests.
