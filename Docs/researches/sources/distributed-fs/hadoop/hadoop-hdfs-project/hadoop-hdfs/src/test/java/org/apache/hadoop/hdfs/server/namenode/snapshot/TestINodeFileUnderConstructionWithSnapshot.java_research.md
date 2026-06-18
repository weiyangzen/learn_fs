# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestINodeFileUnderConstructionWithSnapshot.java

Purpose: Tests snapshot behavior for files being appended or under construction, including snapshot file sizes, block locations, and lease recovery interactions.

Important APIs/types/functions: helpers include `appendFileWithoutClosing` and tests use `HdfsDataOutputStream.hsync(UPDATE_LENGTH)`, `INodeFile.computeFileSize`, `DirectoryDiff`, `DFSClientAdapter.callGetBlockLocations`, `LocatedBlocks`, and `NameNodeAdapter.getLeaseManager/runLeaseChecks`.

Control flow: `testSnapshotAfterAppending` snapshots before/after append and replication changes, checking live inode replication and size. `testSnapshotWhileAppending` snapshots while append streams are open, closes streams later, and verifies snapshot-specific file sizes in directory diffs remain frozen. `testGetBlockLocations` snapshots files before/after appends and verifies snapshot block listings are bounded by captured file length and not marked under construction, while the live file is under construction. `testLease` deletes a directory containing an open file captured by a snapshot and runs lease checks under FSNamesystem write lock.

State and persistence behavior: no restart, but it inspects NameNode in-memory inode/diff state and lease manager behavior. Snapshot state captures open-file length at hsync points.

Dependencies and integration points: integrates append pipeline, block location RPC, snapshot diff internals, leases, FSDirectory, and NameNode locking (`RwLockMode.GLOBAL`).

Risks and test signals: good coverage of open-file snapshot size isolation and block-range correctness. Lease test mostly asserts absence of exception/deadlock, so failure signal is coarse.
