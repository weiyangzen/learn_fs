<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapter.java

Purpose: test-only facade exposing otherwise internal NameNode and FSNamesystem functions to HDFS unit tests.

Important APIs/types/functions: exposes namesystem, RPC server, FSImage-in-HTTP-server swapping, delegation-token manager, heartbeat sending, replication changes, lease manager/lease fields, service state, datanode descriptors, stats, generation stamps, block allocation without journaling, block persistence, stored-block lookup, mkdir edit-log op helpers, safe-mode counters, edits file path lookup, and checkpoint start.

Control flow: methods are thin wrappers around production internals. Some acquire explicit `FSNamesystem` read/write locks with `RwLockMode` before accessing directory or block-manager state. `getFileInfo()` mirrors `FSNamesystem#getFileInfo()` permission-checker setup and lock discipline. `addBlockNoJournal()` creates and saves a block under global write lock, while `persistBlocks()` journals block state under FS write lock.

State and persistence: most methods inspect or mutate live NameNode state. `saveNamespace()`, `abortEditLogs()`, `persistBlocks()`, `addBlockNoJournal()`, and checkpoint helpers affect persistent namespace/edit-log state; other methods expose transient locks, leases, safe-mode counters, and block-manager maps.

Dependencies and integration points: integrates tests with `FSNamesystem`, `FSDirectory`, `FSDirWriteFileOp`, `BlockManagerTestUtil`, `LeaseManager`, `NameNodeHttpServer`, `NNStorage`, and HA/checkpoint protocols.

Risks and test signals: because it bypasses normal API boundaries, callers must preserve lock and journaling expectations. Risks are stale internal coupling, no-journal block additions, and whitebox field access for safe-mode state. Signals are unit tests that need deterministic access to leases, blocks, safemode, edit logs, and HTTP FSImage state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapter.java -->
