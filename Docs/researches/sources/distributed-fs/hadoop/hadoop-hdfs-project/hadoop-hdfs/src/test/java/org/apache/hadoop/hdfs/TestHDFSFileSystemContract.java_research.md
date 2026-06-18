# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSFileSystemContract.java

## Purpose
Runs generic `FileSystemContractBaseTest` coverage against HDFS and adds HDFS-specific append and path-capability checks.

## APIs and Control Flow
`setUp` creates a two-DN `MiniDFSCluster` under a randomized test directory and applies the contract-test umask. `getDefaultWorkingDirectory` returns `/user/<shortUser>`, and `getGlobalTimeout` sets 60 seconds. `testAppend` delegates to `AppendTestUtil.testAppend`. `testFileSystemCapabilities` verifies `DistributedFileSystem` advertises `LEASE_RECOVERABLE` and implements `LeaseRecoverable` and `SafeMode`.

## State, Dependencies, Integration
State is generic filesystem namespace and append data in a mini cluster. Dependencies include `FileSystemContractBaseTest`, `AppendTestUtil`, `CommonPathCapabilities`, AssertJ, and HDFS cluster setup. It integrates public HDFS FS behavior with the common Hadoop FS contract suite.

## Risks and Test Signals
Signals are inherited contract tests plus explicit append and capability assertions. Risks are that capability checks are conditional on `DistributedFileSystem`, so alternate FS wrappers skip them; generic inherited coverage depends on superclass behavior not visible in this file.
