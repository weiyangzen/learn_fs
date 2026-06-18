<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractYarnClusterITest.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractYarnClusterITest.java

## Purpose

`AbstractYarnClusterITest` is the base class for full MapReduce-on-YARN S3A committer integration tests. It manages shared MiniYARN and optional MiniDFS clusters, creates job configurations, applies committer binding/staging options, and exposes scale-test sizing.

## Important APIs, Types, and Functions

- Static `ClusterBinding` holds a cluster name, optional `MiniDFSClusterService`, and `MiniMRYarnCluster`.
- `createCluster(JobConf, boolean)` prepares test config, disables MR history cleanup and NM disk health checks, optionally starts HDFS, starts MiniYARN with two node managers, and returns binding.
- `teardownClusters()` and `terminateCluster()` stop shared clusters.
- `getClusterFS()` returns HDFS if present, otherwise local FS from YARN config.
- `setup()` initializes superclass state, reads scale-test flag, lazily creates cluster binding, and validates it.
- `newJobConf()` starts from YARN config, adds the S3A test config resource, and calls `applyCustomConfigOptions()`.
- `createJob()` creates a named MR job and patches committer configuration.
- `patchConfigurationForCommitter()` sets unique filename policy, S3A committer factory/name, scale-test flag, and local staging temp directory.
- Extension points: `committerName()`, `demandCreateClusterBinding()`, `applyCustomConfigOptions()`, `customPostExecutionValidation()`, and `isUniqueFilenames()`.

## Control Flow and State

Subclasses lazily create a static cluster binding on first setup. Each test gets a JUnit `@TempDir` staging directory, then job configs are derived from the running YARN cluster and patched with the S3A committer and staging options. Scale mode changes mapper/file counts from 1/10 to 10/100.

## State and Persistence Behavior

The cluster binding is static and shared across test methods until `@AfterAll` teardown. Local staging directories are per-test temporary directories. If HDFS is requested, it is a service in the binding and provides the cluster filesystem; otherwise local FS is used.

## Dependencies and Integration Points

It integrates `MiniMRYarnCluster`, optional `MiniDFSClusterService`, S3A committer constants, Hadoop `JobConf`/`Job`, JUnit `@TempDir`, S3A test configuration propagation, and scale-test flags.

## Risks and Edge Cases

Static cluster binding can cause isolation issues if multiple subclasses share the same JVM, so subclasses are expected to control explicit setup/teardown. MiniYARN disk health checks are disabled to avoid false failures in constrained CI. Local staging must be visible to workers for staging committers.

## Test Signals

Signals are produced by subclasses running actual MR jobs. This base contributes validation through successful cluster startup, non-null binding, correct committer config, correctly chosen test file/key counts, and later success-data validation hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractYarnClusterITest.java -->
