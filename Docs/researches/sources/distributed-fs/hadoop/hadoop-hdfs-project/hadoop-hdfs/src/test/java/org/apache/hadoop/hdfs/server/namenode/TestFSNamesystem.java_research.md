<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystem.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystem.java

Purpose: `TestFSNamesystem` covers focused FSNamesystem unit behaviors: duplicate edit-dir normalization, lease cleanup during `clear`, safemode state distinctions, replication queue activation, HA state exposure in namespace info, reset/image-loaded state, layout-version selection, safemode replication configuration, and audit logger initialization.

Important APIs, types, and functions: it uses `FSNamesystem.getNamespaceEditsDirs`, `FSNamesystem.loadFromDisk`, `FSNamesystem.clear`, `FSNamesystem.getEffectiveLayoutVersion`, `BlockManager`, `LeaseManager`, `NamespaceInfo`, `NameNode.initMetrics`, mocked `FSImage`/`FSEditLog`/`NNStorage`, `Whitebox`, and `TopAuditLogger`. The helper `clearNamesystem` wraps `fsn.clear()` in the global write lock and asserts `isImageLoaded` flips false. `DummyAuditLogger` implements `AuditLogger` for config-driven instantiation tests.

Control flow: tests either construct a lightweight FSNamesystem around mocked storage/edit log or build/format a small real namespace. Safemode tests manually call `enterSafeMode` and `leaveSafeMode` and assert startup-vs-low-resource semantics. Replication queue activation spies the FSNamesystem and mocks HA context/state so `shouldPopulateReplQueues` returns true, then observes `BlockManager.isPopulatingReplQueues` across first and later safemode transitions. Audit logger tests mutate the same `Configuration` through several combinations of default, top, and custom logger strings and assert resulting logger types.

State and persistence behavior: the file tests in-memory namesystem state rather than full persistence, except `testFSNamespaceClearLeases`, which formats a NameNode directory and loads the namesystem from disk before adding a synthetic lease. It verifies reset clears namespace children, leases, and image-loaded state, then allows image-load completion again.

Dependencies and integration points: depends on metrics initialization, HA service state, block management, audit logger plugin loading, caller-context configuration, and filesystem cleanup under `MiniDFSCluster.getBaseDirectory`.

Risks and edge cases: use of `Whitebox` and Mockito against internal fields makes tests sensitive to refactors. `testInitAuditLoggers` reuses mutable `Configuration`, so prior settings can affect later cases unless deliberately overwritten. Some assertions use boolean expressions inside `assertTrue` instead of more precise assertions, making failure messages less diagnostic.

Test signals: exact edit-dir count, lease count before/after clear, safemode boolean transitions, replication queue activation state, non-null HA state in `NamespaceInfo`, effective layout-version matrix, private safe-replication value, and audit logger list size/type composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystem.java -->
