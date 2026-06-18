# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletion.java

Purpose: Tests ordered snapshot deletion marking, hidden system xattr behavior, persistence, and behavior when xattrs are disabled or pre-existing user xattrs exist.

Important APIs/types/functions: enables `DFS_NAMENODE_SNAPSHOT_DELETION_ORDERED`. Static helpers `assertMarkedAsDeleted`, `assertNotMarkedAsDeleted`, and `getDeletedSnapshotName` inspect `Snapshot.Root.isMarkedAsDeleted`, `XAttrFeature`, `XATTR_SNAPSHOT_DELETED`, and `hdfs.getSnapshotListing`. `assertXAttrSet` deletes a snapshot by its active/deleted listing name and validates internal and user-visible xattrs.

Control flow: `testOrderedSnapshotDeletion` creates `s0/s1/s2`, deletes later snapshots first, verifies they are marked deleted/renamed rather than immediately removed, then deletes remaining names. Persistence tests repeat deletion, restart NameNodes, or saveNamespace before restart. Disabling-xattr test toggles `dfs.namenode.xattrs.enabled` false after marking and verifies internal deletion xattr still works while user xattr operations fail. Pre-existing xattr test ensures user xattrs remain visible while system deletion marker is hidden.

State and persistence behavior: ordered deletion stores state as renamed snapshot roots with system xattr and `Snapshot.Root` deleted flag; tests check survival across restart and fsimage save.

Dependencies and integration points: integrates snapshot listing, xattr subsystem, fsimage restart, and ordered snapshot deletion config.

Risks and test signals: strong internal/external visibility checks. `getDeletedSnapshotName` assumes a listing entry starts with the requested base name and will fail if listing semantics change.
