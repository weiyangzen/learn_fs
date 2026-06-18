# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreMountTable.java

Purpose: `TestStateStoreMountTable` validates the `MountTableStore` API used by RBF routers to persist and query federated mount-table entries. It extends `TestStateStoreBase`, builds a two-nameservice fixture from `FederationTestUtils.NAMESERVICES`, and clears all `MountTable` records before each test.

Important APIs and helpers: it exercises `AddMountTableEntryRequest/Response`, `UpdateMountTableEntryRequest/Response`, `RemoveMountTableEntryRequest`, `GetMountTableEntriesRequest/Response`, and `QueryResult<MountTable>`. Helper `getMountTableEntry()` queries one source path and returns the first sorted result; helper `getMountTableEntries()` requires a non-null root path and returns records plus the state-store response timestamp.

Control flow and state behavior: `testSynchronizeMountTable()` bulk synchronizes mock entries, reloads the mount-store cache, and confirms default destination preservation. `testAddMountTableEntry()` proves the empty store gains one visible entry after an add and cache reload. `testRemoveMountTableEntry()` bulk inserts, removes by `srcPath`, reloads, and checks the count decreases. `testUpdateMountTableEntry()` inserts an entry, verifies the original nameservice, replaces the same source path with a new destination map, and verifies the update is visible.

Persistence and cache semantics: write APIs operate against the state-store driver, while reads are cache-backed and require `mountStore.loadCache(true)` in the tests before assertions. The tests show mount-table records are keyed by source path and that updating a source path replaces destination metadata without adding an extra row.

Dependencies and integration points: the test uses `FederationStateStoreTestUtils.createMockMountTable()` and `synchronizeRecords()` for fixture construction, state-store protocol classes for API coverage, and `verifyException()` for disconnected-driver checks. It integrates with `StateStoreService` and the configured test driver through the base class.

Risks and test signals: disconnected-driver behavior expects add, update, remove, and even cached get after explicit cache load to throw `StateStoreUnavailableException`. The assertions are mostly count and default-destination checks; they do not deeply validate ordering beyond the helper comment that shortest mount string sorts first.
