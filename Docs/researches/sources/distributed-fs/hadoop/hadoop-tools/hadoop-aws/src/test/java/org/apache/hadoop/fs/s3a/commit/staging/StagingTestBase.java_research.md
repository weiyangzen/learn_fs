# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/StagingTestBase.java

## Purpose
Shared fixture and mock infrastructure for staging committer unit tests. It binds mock S3A filesystems, creates mock AWS SDK clients, tracks MPU operations, injects failures, manages a MiniDFS cluster, and provides base classes for job and task committer tests.

## Important APIs, Types, and Functions
Static fixture methods include `createAndBindMockFSInstance()`, `lookupWrapperFS()`, path existence/delete stubbing helpers, `assertConflictResolution()`, `createTestOutputFiles()`, and `newMockS3Client()`. Nested classes include `MiniDFSTest`, `JobCommitterTest<C>`, `TaskCommitterTest<C>`, `ClientResults`, and `ClientErrors`. The mock client handles `createMultipartUpload`, `uploadPart`, `completeMultipartUpload`, `abortMultipartUpload`, `deleteObject`, and `listMultipartUploads`.

## Control Flow and Behavior
`createAndBindMockFSInstance()` creates a mocked `S3AFileSystem` with mocked internals/store/client, wraps it in `MockS3AFileSystem`, initializes it at `s3a://bucket/`, stores qualified output paths, and registers it with `FileSystemTestHelper`. `JobCommitterTest.setupJob()` creates a job config with a committer UUID, disables success marker creation, creates `ClientResults`/`ClientErrors`, binds a mock client, and constructs a `JobContext`. `TaskCommitterTest.setupTask()` creates the job committer, runs `setupJob()`, creates a task context, and configures local buffer and staging paths. `newMockS3Client()` records requests and can throw configured `AwsServiceException`s at specific operation counts, optionally recovering after the first failure.

## State, Persistence, and Dependencies
State is held in static output path/URI/root fields, MiniDFS cluster service state, per-test mock result/error containers, mock S3 active upload maps, pending local/HDFS files, and configured job/task contexts. Dependencies include Mockito, AWS SDK v2 S3 models/client, `MockS3AFileSystem`, `MiniDFSClusterService`, MR contexts, and Hadoop filesystem test helpers.

## Integration Points, Risks, and Test Signals
This base class is the backbone of staged committer unit coverage. It provides deterministic signals for MPU request counts, abort/commit behavior, destination key generation, and cleanup without real S3. Risks include mock drift from actual S3/S3A behavior, shared static paths across tests, and concurrency assumptions in synchronized mock-client handlers.
