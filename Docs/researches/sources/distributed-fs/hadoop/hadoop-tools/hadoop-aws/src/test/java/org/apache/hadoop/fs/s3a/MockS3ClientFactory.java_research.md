# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3ClientFactory.java

## Purpose

Mockito-backed `S3ClientFactory` for unit tests that need an S3A filesystem to initialize without talking to AWS. It supplies mocked sync, async, and transfer-manager clients with enough default behavior for startup.

## Important APIs, Types, and Functions

Implements `S3ClientFactory.createS3Client()`, `createS3AsyncClient()`, and `createS3TransferManager()`. The sync client stubs `listMultipartUploads()` to return an empty non-truncated response and `getBucketLocation()` to return `us-west-2`.

## Control Flow

Each factory method creates a Mockito mock and returns it. The sync client has fixed stubs for multipart purge checks and bucket-region discovery; async client and transfer manager have no behavior beyond mock identity.

## State, Dependencies, and Integration Points

There is no persistent state. The class depends on AWS SDK v2 S3 model builders, `Region.US_WEST_2`, Mockito, and S3A client creation parameters. It integrates with tests that configure S3A to use a custom client factory during initialization.

## Risks and Test Signals

The stubbed region and empty MPU list can mask tests that need other startup behavior. It should be extended only with targeted stubs so it remains a low-friction initialization mock. Failures usually signal changed S3A startup calls or AWS SDK method signatures.
