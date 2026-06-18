# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFSStoragePolicyCommands.java

## Purpose
`TestViewFSStoragePolicyCommands` reuses the storage-policy command suite with a ViewFileSystem default filesystem and adds ViewFS-specific root and scheme-qualified path coverage.

## Important APIs, Types, And Functions
It extends `TestStoragePolicyCommands` and uses `MiniDFSNNTopology.simpleFederatedTopology`, `ConfigUtil.addLink`, `FsConstants.VIEWFS_SCHEME`, `DistributedFileSystem`, `WebHDFS` URI construction, and `StoragePolicyAdmin`.

## Control Flow
The overridden setup starts a federated two-NameNode cluster, creates `/user1` and `/user2` on separate filesystems, sets `fs.defaultFS` to `viewfs://cluster`, mounts `/foo` and `/hdfs2`, and initializes `fs = FileSystem.get(conf)`. Additional tests assert that storage-policy operations on `/` fail under ViewFS, and that hdfs:// and webhdfs:// URI-qualified paths still support set/get/unset.

## State, Persistence, And Dependencies
State is in the ViewFS mount table and underlying HDFS namespace. It inherits static cluster/fs fields from the base class and relies on base teardown.

## Integration Points
The test checks `StoragePolicyAdmin` behavior through ViewFS mount resolution, federated HDFS targets, direct HDFS URI handling, and WebHDFS path handling.

## Risks
Root failure output is tied to ViewFS exception wording. WebHDFS URI construction uses the NameNode HTTP host and port, which depends on MiniDFSCluster HTTP setup. Inherited base tests now execute against ViewFS-mounted paths, so failures can originate from mount resolution rather than storage policy logic.

## Test Signals
Signals include root command failure with "not supported for filesystem viewfs", inherited storage-policy command successes, and explicit set/get/unset output for hdfs:// and webhdfs:// paths.
