<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/StubS3ClientFactory.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/StubS3ClientFactory.java


## Purpose
Stub S3ClientFactory returning preconfigured sync, async, and transfer-manager clients while counting creations.


## Important APIs, Types, and Functions
StubS3ClientFactory defines STUB_FACTORY, constructor-injected S3Client/S3AsyncClient/S3TransferManager/launcher, createS3Client(), createS3AsyncClient(), createS3TransferManager(), creation-count getters, and toString().


## Control Flow
Sync and async client creation increment counters, invoke the launcher hook for injected delay/failure, then return supplied clients. Transfer manager creation only increments and returns the supplied manager.


## State and Persistence Behavior
State is injected clients, launcher, and AtomicInteger counters. No null checks are performed, so null clients are deliberate failure hooks.


## Dependencies and Integration Points
Depends on S3ClientFactory, AWS SDK S3 sync/async clients, S3TransferManager, URI, and InvocationRaisingIOE.


## Risks and Test Signals
Risks are launcher side effects and test fragility if factory API changes. Signals support tests for lazy client construction, retry on factory failures, and creation-count assertions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/StubS3ClientFactory.java -->
