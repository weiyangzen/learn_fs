# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestWebHDFSStoragePolicyCommands.java

## Purpose
`TestWebHDFSStoragePolicyCommands` runs the base storage-policy command tests using a WebHDFS filesystem as the default filesystem.

## Important APIs, Types, And Functions
It extends `TestStoragePolicyCommands` and uses `WebHdfsTestUtil.getWebHdfsFileSystem`, `WebHdfsConstants.WEBHDFS_SCHEME`, and `FS_DEFAULT_NAME_KEY`.

## Control Flow
The overridden setup calls the base HDFS cluster setup, replaces `fs` with a WebHDFS filesystem, and points `fs.defaultFS` at its URI. The inherited tests then execute set/get/unset policy commands through WebHDFS paths.

## State, Persistence, And Dependencies
State is inherited from the base cluster and stored through WebHDFS calls into the same NameNode namespace. Base teardown closes the filesystem and cluster.

## Integration Points
This connects `StoragePolicyAdmin` to WebHDFS path resolution and REST-backed filesystem operations while reusing the HDFS storage-policy assertions.

## Risks
Because it only overrides setup, diagnosis requires understanding the base class. WebHDFS server availability and URI qualification can cause failures outside storage-policy metadata logic.

## Test Signals
Signals are inherited from `TestStoragePolicyCommands`: successful set/get/unset operations, missing-path failures, and policy/unspecified output, all executed with WebHDFS as default FS.
