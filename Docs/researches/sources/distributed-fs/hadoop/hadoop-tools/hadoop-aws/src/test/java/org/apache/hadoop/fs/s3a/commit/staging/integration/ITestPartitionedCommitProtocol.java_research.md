# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestPartitionedCommitProtocol.java

## Purpose
Integration protocol suite specialization for `PartitionedStagingCommitter`.

## Important APIs, Types, and Functions
The class extends `ITestStagingCommitProtocol`, returns `COMMITTER_NAME_PARTITIONED`, creates `PartitionedStagingCommitter`, and defines a fault-injecting committer wrapper. It overrides `testMapFileOutputCommitter()` to skip because the partitioned committer is not suitable for map output.

## Control Flow and Behavior
Inherited protocol tests run against the partitioned committer except the map-file output case. The failing committer class delegates lifecycle methods through `CommitterFaultInjectionImpl` before calling the superclass methods, enabling shared failure recovery tests.

## State, Persistence, and Dependencies
State is inherited staging task/job metadata and S3A output. Dependencies include partitioned and directory staging committer classes, fault-injection interfaces, and the abstract protocol test suite.

## Integration Points, Risks, and Test Signals
This file asserts that the partitioned committer honors the shared S3A committer protocol where applicable. The explicit skip documents an unsupported output format scenario and prevents a false failure from an incompatible test.
