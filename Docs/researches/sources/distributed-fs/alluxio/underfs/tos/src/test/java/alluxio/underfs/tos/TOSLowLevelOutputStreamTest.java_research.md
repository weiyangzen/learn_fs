# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSLowLevelOutputStreamTest.java

## Purpose
This PowerMock/Mockito suite verifies the streaming TOS upload implementation's small-object and multipart boundaries.

## Important Tests
`writeByte`, `writeByteArrayForSmallFile`, and `createEmptyFile` verify that small or empty writes use `putObject` rather than multipart upload. `writeByteArrayForLargeFile` writes one byte over the 8 MiB partition size and expects multipart creation, two executor submissions, completion, and multipart ETag. `flush` verifies upload tasks are submitted and waited for before close. `close` checks empty close behavior and content hash.

## Dependencies and Integration
The test configures `UNDERFS_TOS_STREAMING_UPLOAD_PARTITION_SIZE` and `UNDERFS_TOS_STREAMING_UPLOAD_ENABLED`, mocks `TOSV2`, `ListeningExecutorService`, and SDK output types, and relies on the superclass upload scheduling behavior.

## Signals and Gaps
Coverage establishes the partition threshold and content hash paths. It does not cover failed part upload, abort-on-error, ordering of uploaded parts under true concurrency, or SDK exception conversion in all multipart operations.
