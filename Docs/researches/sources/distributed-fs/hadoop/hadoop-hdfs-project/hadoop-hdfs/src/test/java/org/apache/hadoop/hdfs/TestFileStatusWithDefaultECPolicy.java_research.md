# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithDefaultECPolicy.java

## Purpose
Tests that HDFS file status and client file info correctly report erasure-coding policy state for directories and files when the default system EC policy is used.

## APIs and Control Flow
`before` creates a one-DN `MiniDFSCluster`, obtains `DistributedFileSystem` and `DFSClient`, and enables `getEcPolicy()`. `getEcPolicy` returns `StripedFileTestUtil.getDefaultECPolicy`. `testFileStatusWithECPolicy` creates `/foo`, verifies no EC policy initially on directory or file, sets the EC policy on the directory, verifies the directory policy through `DFSClient.getFileInfo`, creates a child file, and checks inherited EC status through `FileStatus`, `HdfsFileStatus`, and `ContractTestUtils`.

## State, Dependencies, Integration
State is namespace metadata for EC policy inheritance. It depends on `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `ErasureCodingPolicy`, `FsPermission`, and `ContractTestUtils`. It integrates EC policy management with status reporting and string rendering.

## Risks and Test Signals
Signals include explicit null/non-null policy checks and `FileStatus#toString` containing `isErasureCoded=true`. Risks are running a striped-policy test on a one-DN cluster where policy metadata is tested but full striped IO is not.
