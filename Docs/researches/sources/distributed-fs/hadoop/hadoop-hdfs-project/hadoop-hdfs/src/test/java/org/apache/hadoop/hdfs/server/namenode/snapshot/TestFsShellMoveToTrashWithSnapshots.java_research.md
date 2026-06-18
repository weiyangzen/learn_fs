# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFsShellMoveToTrashWithSnapshots.java

Purpose: Stress-tests FsShell move-to-trash behavior while snapshots, snapshot deletions, and many renames reshape paths.

Important APIs/types/functions: uses `SnapshotTestHelper.MyCluster` with trash enabled by `fs.trash.interval`. `MyDirs` tracks a renameable nested path with `TO_BE_REMOVED` segments. `MyFile` tracks temp, destination, and trash paths. Operation classes `MoveToTrashOp` and `DeleteSnapshotOp` are shuffled and executed once through `Op.execute`.

Control flow: `runTestMoveToTrashWithShell` creates db/tmp dirs, swaps nested directories through snapshot-protected renames, creates temp bucket files, moves older temp files into destination dirs, performs more nested renames, queues a move-to-trash for the database directory, and interleaves snapshot deletion operations in random order. Multi-task tests run many scenarios concurrently with a fixed thread pool, then assert all bucket files exist at normalized trash/current paths.

State and persistence behavior: no NameNode restart. State stress is live namespace state plus snapshot diffs and FsShell trash rename behavior. `updateTrashPath` compensates for trash root prefixes chosen by shell output.

Dependencies and integration points: integrates `FsShell -rm -r`, `TrashPolicyDefault` logging, snapshot creation/deletion, rename semantics, concurrency utilities, and HDFS path resolution.

Risks and test signals: high-value stress for race/order interactions and path rewrite correctness. Random shuffling and sleeps broaden coverage but complicate reproducibility; assertions mostly prove file reachability, not exact trash tree shape.
