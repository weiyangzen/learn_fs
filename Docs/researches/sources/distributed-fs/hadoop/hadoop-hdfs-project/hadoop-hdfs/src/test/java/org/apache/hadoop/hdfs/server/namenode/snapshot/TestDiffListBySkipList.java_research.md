# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDiffListBySkipList.java

Purpose: Tests `DiffListBySkipList`, the skip-list implementation of directory snapshot diffs, against `DiffListByArrayList` and real HDFS directory snapshot behavior.

Important APIs/types/functions: `newDiffListBySkipList()` initializes `DirectoryDiffListFactory` with interval 3 and `MAX_LEVEL`. Helpers include `verifyChildrenList`, `getCombined`, `getChildrenList`, `addDiff`, `remove`, `assertDirectoryDiff`, `assertSkipList`, and `assertSkipListNode`. It directly uses `DirectoryWithSnapshotFeature.DirectoryDiff`, `ChildrenDiff`, `DiffList`, `DiffListByArrayList`, and `SkipListNode`.

Control flow: tests create zero-datanode clusters, make snapshottable roots, then create/delete child directories between 100 snapshots. `testAddLast` adds diffs in chronological order; `testAddFirst` adds reverse-ordered diffs; removal tests delete from tail, head, random positions, lower skip-list levels, and upper levels. After each mutation, the skip list is compared with array-list behavior and HDFS `INodeDirectory.getChildrenList`.

State and persistence behavior: this is in-memory structural testing, not fsimage persistence. Snapshot diffs are generated from live NameNode state, and deletion calls `hdfs.deleteSnapshot` to keep the backing directory diffs aligned with test removals.

Dependencies and integration points: integrates `FSDirectory`, `INodeDirectory`, snapshot diff internals, `ReadOnlyList`, and HDFS snapshot creation/deletion.

Risks and test signals: verifies both semantic output (children lists for ranges) and structural invariants (skip node targets and combined diffs). Random removal adds coverage but can make reproduction require logs/seed.
