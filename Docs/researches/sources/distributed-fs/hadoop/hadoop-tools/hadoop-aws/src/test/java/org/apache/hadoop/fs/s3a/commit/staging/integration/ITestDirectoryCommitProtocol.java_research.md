# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestDirectoryCommitProtocol.java

## Purpose
Integration protocol suite specialization for `DirectoryStagingCommitter`. It runs shared low-level committer protocol tests with directory committer behavior and validates default staging conflict configuration.

## Important APIs, Types, and Functions
The class extends `ITestStagingCommitProtocol`, returns `COMMITTER_NAME_DIRECTORY`, creates `DirectoryStagingCommitter`, disables experimental IO statistics collection, and defines a `CommitterWithFailedThenSucceed` using `CommitterFaultInjectionImpl`.

## Control Flow and Behavior
Shared protocol tests come from the superclass hierarchy. This class creates real directory staging committers for those tests and provides a fault-injecting variant for retry/failure cases. `testValidateDefaultConflictMode()` reads the default conflict mode from a base `Configuration` and the active filesystem config, asserting both are `append`.

## State, Persistence, and Dependencies
State includes staging local/HDFS pending metadata and S3A output from inherited integration tests. Dependencies include directory committer, fault injection, S3A committer constants, and the shared staging protocol suite.

## Integration Points, Risks, and Test Signals
The test confirms the directory committer conforms to the same protocol expectations as other S3A committers while preserving directory-specific config defaults. Failures commonly indicate config override leakage or lifecycle differences in setup/task/job commit.
