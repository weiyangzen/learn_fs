# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithDFSAdmin.java

## Purpose
`TestViewFileSystemOverloadSchemeWithDFSAdmin` verifies that `DFSAdmin` commands operate correctly when the `hdfs` scheme is overloaded by `ViewFileSystemOverloadScheme` with configured mount links.

## Important APIs, Types, And Functions
It uses `ViewFileSystemOverloadScheme`, `ViewFsTestSetup.addMountLinksToConf`, `DFSAdmin`, `ToolRunner`, `MiniDFSCluster`, `DistributedFileSystem`, `CommonConfigurationKeys`, and captured stdout/stderr helpers `assertOutMsg`/`assertErrMsg`.

## Control Flow
Setup configures `fs.hdfs.impl` to ViewFS overload and the target HDFS implementation to `DistributedFileSystem`, starts a cluster, and records the default hdfs URI. Tests add HDFS and local mount links, then run `DFSAdmin` with and without `-fs` for `-safemode`, `-saveNamespace`, `-allowSnapshot`, `-disallowSnapshot`, and `-setBalancerBandwidth`. Negative tests use an unknown host target and a local filesystem mount.

## State, Persistence, And Dependencies
State includes the ViewFS mount table in configuration, the MiniDFSCluster NameNode state, local target directory, safe-mode state, snapshot permission state, and captured stream buffers. `FileSystem.closeAll()` is called during teardown.

## Integration Points
This covers DFSAdmin command dispatch through an overloaded `hdfs` scheme, fallback target FS behavior, mounted local filesystem rejection, and administrative RPCs reaching the underlying HDFS filesystem.

## Risks
It assumes the default filesystem URI's host names the mount table. Error and success assertions depend on output line positions. Safe mode is entered and left in tests, so cleanup after failures matters for later tests.

## Test Signals
Signals include return codes, "Save namespace successful", safe-mode status, UnknownHostException text, local filesystem rejection text, snapshot command success messages, and balancer bandwidth output.
