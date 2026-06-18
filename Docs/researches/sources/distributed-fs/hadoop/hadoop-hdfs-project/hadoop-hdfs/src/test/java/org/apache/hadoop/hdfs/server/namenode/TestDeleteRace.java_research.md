# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeleteRace.java

Purpose: Regression coverage for races between delete/rename and block allocation, lease recovery, commit block synchronization, open access-time updates, and snapshot diff state.

Important APIs/types/functions: Uses custom `SlowBlockPlacementPolicy`, `SubjectInheritingThread` delete/rename workers, `SnapshotTestHelper`, `DelayAnswer`, spied `DatanodeProtocolClientSideTranslatorPB.commitBlockSynchronization`, `FSNamesystem.renameTo`, `getBlockLocations`, `RwLockMode`, and snapshot manager APIs.

Control flow: Delete/add-block tests slow target selection, delete the file concurrently, and expect writer `hsync` failure, with and without snapshots. Rename race writes while renaming a parent and restarts the NameNode. Commit synchronization tests delay DataNode commit RPC, delete an ancestor, optionally recreate directories, then allow commit and restart NameNodes. Other tests cover lease hard-limit recovery after deleting a snapshotted open file, ordered open/rename lock interleaving, and failed deletion of a snapshottable directory.

State and persistence behavior: Stresses namespace mutations while block and lease state are mid-transition. Restart checks ensure edit logs remain replayable after races. Snapshot tests ensure retained deleted inodes do not corrupt lease recovery or diff reporting.

Dependencies and integration points: Integrates block placement, NameNode locks, lease manager, DataNode recovery RPC, snapshots, edit logging, access-time updates, and FSDirectory removal behavior.

Risks: Timing-sensitive tests rely on sleeps, semaphores, and injected delays. Some paths deliberately reinsert a deleted inode into `INodeMap` through Whitebox.

Test signals: Expected stale-write exceptions, successful NameNode restarts, no propagated commit failure, changed access time after open/rename ordering, successful snapshot diff report, and expected snapshottable-directory count.
