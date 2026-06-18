# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileContextSnapshot.java

Purpose: Verifies snapshot operations exposed through `FileContext` rather than `DistributedFileSystem`.

Important APIs/types/functions: setup creates a `MiniDFSCluster` with block size 1024 and replication 3, obtains `FileContext.getFileContext(conf)` and a `DistributedFileSystem`, and creates `/snapshot`. Tests call `fileContext.createSnapshot`, `deleteSnapshot`, and `renameSnapshot`; `DistributedFileSystem` is used for setup and status assertions.

Control flow: `testCreateAndDeleteSnapshot` creates a file, disallows snapshots, expects `FileContext.createSnapshot` to throw `SnapshotException` containing "Directory is not a snapshottable directory", then allows snapshots, creates `s1`, verifies the snapshot path exists, deletes it, and verifies removal. `testRenameSnapshot` records `FileStatus` for `.snapshot/s1/file1`, renames `s1` to `s2`, verifies old path gone/new path present, then checks status equality after normalizing the path.

State and persistence behavior: no restart or fsimage persistence. It validates API-layer path/status behavior during a live NameNode session.

Dependencies and integration points: covers `FileContext` bindings to HDFS snapshot APIs, `SnapshotTestHelper.getSnapshotRoot`, and `FileStatus` equality semantics.

Risks and test signals: focused API smoke test. It intentionally compares status string after path normalization to ensure snapshot rename changes only the path, but it does not verify block/checksum identity.
