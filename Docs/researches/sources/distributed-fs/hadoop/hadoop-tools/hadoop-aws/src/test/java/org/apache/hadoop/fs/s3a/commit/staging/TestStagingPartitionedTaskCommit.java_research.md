# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedTaskCommit.java

## Purpose
Mocking tests for partitioned staging task commit conflict handling and destination key generation.

## Important APIs, Types, and Functions
The class extends `TaskCommitterTest<PartitionedStagingCommitter>`. It uses `createTestOutputFiles()`, `PartitionedStagingCommitter.commitTask()`, `ConflictResolution`, `CreateMultipartUploadRequest`, and `Paths.addUUID()`.

## Control Flow and Behavior
`@BeforeAll` builds a static set of four partitioned relative files. Bad conflict mode is rejected. Default mode resolves to append. Fail mode creates task output files, mocks one existing partition to force `PathExistsException`, then retries with no conflict and verifies uploads. Append mode succeeds even with an existing partition. Replace mode also succeeds with an existing partition; deletion behavior is noted as a TODO at task level. `verifyFilesCreated()` asserts one MPU request per relative file and exact expected destination keys, including UUID suffixing when enabled.

## State, Persistence, and Dependencies
State is local task output files and mock S3 create-MPU requests. Dependencies include partitioned committer conflict config, staging test fixture, and AWS SDK request models.

## Integration Points, Risks, and Test Signals
The suite ensures task commit only uploads intended files and handles partition conflicts according to mode. It is a key signal for destination key construction, particularly unique filename policy with partitioned relative paths.
