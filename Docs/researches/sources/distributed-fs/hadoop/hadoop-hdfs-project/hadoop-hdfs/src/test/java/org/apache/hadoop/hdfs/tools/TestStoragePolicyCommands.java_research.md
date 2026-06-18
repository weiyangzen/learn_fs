# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicyCommands.java

## Purpose
`TestStoragePolicyCommands` verifies `StoragePolicyAdmin` set, get, and unset command behavior against HDFS paths, including URI-qualified paths and missing-path failures.

## Important APIs, Types, And Functions
The class uses `StoragePolicyAdmin`, `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.toolRun`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, `StorageType`, and `StoragePolicySatisfierMode.EXTERNAL`.

## Control Flow
`clusterSetUp()` creates a one-DataNode cluster with ARCHIVE and DISK storage types and an external SPS mode. Tests create nested files, run storage policy commands with absolute and URI-qualified paths, compare expected command output for WARM/COLD/HOT policies, unset policies, and verify unspecified-policy output after unsetting.

## State, Persistence, And Dependencies
State is HDFS namespace metadata: explicit storage policies on directories/files and default unspecified policies. Cluster and filesystem are closed in teardown.

## Integration Points
The test covers `StoragePolicyAdmin` CLI parsing, filesystem path qualification, NameNode storage-policy metadata APIs, and default policy suite string formatting.

## Risks
Expected output includes `BlockStoragePolicy.toString()` formatting and exact path qualification. The static `conf`, `cluster`, and `fs` fields support subclass reuse but can leak if teardown fails.

## Test Signals
Signals are `DFSTestUtil.toolRun` return codes, expected success messages, policy descriptions from `BlockStoragePolicySuite`, missing path errors, and unspecified-policy output.
