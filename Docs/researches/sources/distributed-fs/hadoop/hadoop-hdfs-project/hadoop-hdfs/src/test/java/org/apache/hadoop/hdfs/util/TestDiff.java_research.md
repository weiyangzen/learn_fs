# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestDiff.java

Purpose: randomized stress coverage for `Diff<byte[], INode>`, the utility used by NameNode snapshot/directory diff logic.

Important APIs/types/functions: `Diff.create/delete/modify`, undo methods, `combinePosterior`, `apply2Previous`, `apply2Current`, `accessPrevious`, `accessCurrent`, `Diff.search`, `Diff.Container`, `Diff.UndoInfo`, `INodeDirectory`.

Control flow: `testDiff` runs combinations of starting list size and modification count from 0 to 10000 using exponential steps. `runDiffTest` builds a sorted previous inode list, copies it into current, creates five incremental diffs, then randomly creates, deletes, or modifies inodes while recording each operation. It verifies that applying diffs forward reproduces current, applying them backward reproduces previous, combining all diffs preserves both directions, and key-based access returns the identical object expected from previous/current. Each mutation occasionally records `toString`, undoes, asserts original diff text, reapplies, and asserts restored diff text.

State and persistence behavior: all state is in-memory `INodeDirectory` objects with deterministic names and mutable modification time. Randomness drives operation choice and undo sampling; there is no fixed seed.

Dependencies and integration points: depends on NameNode inode classes, `PermissionStatus`, `DFSUtil.string2Bytes`, and snapshot diff container behavior. It is an integration-style unit test for low-level diff invariants relied on by snapshots.

Risks: randomized coverage can be non-reproducible; failures may need captured stdout parameters. Identity checks are stricter than equality and protect against object replacement bugs.

Test signals: forward/backward application equivalence, combined diff equivalence, previous/current key access, search insertion order, and undo/redo stability.
