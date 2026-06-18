<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataConcurrentTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataConcurrentTest.java

**Purpose:** Tests concurrent metadata sync deduplication for `InodeSyncStream`, ensuring overlapping syncs are skipped or allowed according to path relationship, recursion, force/load flags, sync interval, cancellation, and `shouldSync`.

**Important APIs/types/functions:** Uses `InodeSyncStream.sync`, `SyncStatus.OK`, `SyncStatus.NOT_NEEDED`, `LockingScheme`, `UfsSyncPathCache` via `mFileSystemMaster.getSyncPathCache`, `DescendantType.ALL/ONE`, `FileSystemMasterCommonPOptions.syncIntervalMs`, and `CompletableFuture`.

**Control flow:** `before` enables `MASTER_METADATA_CONCURRENT_SYNC_DEDUP`, creates a 2-branch, 3-level UFS hierarchy, slows UFS operations, and confirms only root inode exists. Tests launch two sync streams with staggered futures. Same directory or parent/subdirectory overlaps are skipped when dedup applies; different directories sync concurrently. Sequential syncs can happen twice when intervals permit. Negative sync interval scenarios return `NOT_NEEDED`. A cancellation test cancels the second overlapping sync and then verifies a later sync is not deadlocked. `syncWhenShouldSyncIsSetTrue` constructs locking schemes with shouldSync true and verifies dedup does not suppress those syncs.

**State and persistence behavior:** Syncs load UFS directory hierarchy into inode metadata. Assertions compare inode counts, especially expected full tree size. Dedup state lives in sync-path cache and must be released after completion or cancellation.

**Dependencies and integration points:** Extends `FileSystemMasterSyncMetadataTestBase`, uses PowerMock for UFS factory preparation, a slow mock/test UFS, Alluxio locking scheme, sync path cache, and async execution.

**Risks:** Timing uses fixed sleeps of 10ms and 100ms around futures plus UFS slow time, so scheduling changes can affect overlap. Dedup semantics are complex and path relationship dependent. Cancellation behavior is critical for avoiding leaked sync-path locks.

**Test signals:** Expected `(OK, NOT_NEEDED)`, `(OK, OK)`, or `(NOT_NEEDED, NOT_NEEDED)` result pairs; inode count equals root-only, one-level loaded, or full expected tree as appropriate; post-cancellation sync returns OK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataConcurrentTest.java -->
