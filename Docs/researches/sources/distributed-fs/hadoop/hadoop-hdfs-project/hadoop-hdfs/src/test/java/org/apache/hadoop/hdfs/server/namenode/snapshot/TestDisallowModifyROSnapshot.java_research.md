# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDisallowModifyROSnapshot.java

Purpose: Verifies that paths inside read-only HDFS snapshots reject mutating filesystem operations with `SnapshotAccessControlException`.

Important APIs/types/functions: class-level setup creates `/TestSnapshot/sub1/dir1`, `/TestSnapshot/sub2/dir2`, snapshots `sub1` as `testSnapshot`, and stores the snapshot path to `dir1`. Tests call `DistributedFileSystem` methods such as `setReplication`, `setPermission`, `setOwner`, `rename`, `delete`, `setQuota`, `setTimes`, `append`, and `mkdirs`, plus deprecated `DFSClient.create` and `createSymlink`.

Control flow: each test attempts one mutation against `objInSnapshot` or an operation whose destination is inside `.snapshot`. Most use `assertThrows(SnapshotAccessControlException.class)`. `testRename` covers source-in-snapshot, destination-in-snapshot, and `rename` with `Options.Rename`.

State and persistence behavior: no restart path is covered. The shared static cluster persists for the class, with one snapshot object reused across all mutation tests.

Dependencies and integration points: exercises the filesystem API and lower-level `DFSClient` entry points to ensure snapshot read-only enforcement is not bypassed outside `DistributedFileSystem`.

Risks and test signals: good API surface coverage for mutation rejection. Since it reuses static state, a setup failure affects every test. The symlink case targets `"/TestSnapshot/sub1/.snapshot"` rather than the exact saved object path, covering mutation under the reserved snapshot directory.
