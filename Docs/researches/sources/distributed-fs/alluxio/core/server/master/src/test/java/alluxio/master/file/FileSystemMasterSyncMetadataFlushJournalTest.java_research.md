<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataFlushJournalTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataFlushJournalTest.java

**Purpose:** Verifies metadata sync journal merging/flushing behavior for hierarchical and flat UFS trees, including successful load/update/delete cycles and failure paths.

**Important APIs/types/functions:** Uses `InodeSyncStream.sync`, custom `TestInodeSyncStream`, `FileSystemMergeJournalContext`, `FileSystemJournalEntryMerger`, `MetadataSyncMergeJournalContext`, custom `TestJournalContext`, `LockingScheme`, `RpcContext`, `InternalOperationContext`, and `DescendantType.ALL`.

**Control flow:** `hierarchicalDirectory` and `flatDirectory` call `run` with different tree shapes. `run` creates UFS hierarchy, syncs it with a spying merge journal context, disables further appending/flushing after sync, verifies all metadata-sync journal mergers are empty, and checks inode counts and journal count bounds. It then recreates UFS with newer timestamps and expects delete/recreate-style file journal entries, then deletes all UFS content and expects Alluxio inode count to return to root. Failure tests inject failed UFS paths for a hierarchical child or root and validate failed sync status or thrown runtime while still flushing collected metadata-sync journals.

**State and persistence behavior:** Tests inode store population, direct-children-loaded flags for directories, completed flags for files, journal append accumulation, pending flush clearing, and exactly one flush per sync phase when pending entries exist. It explicitly verifies no metadata-sync merged journal entries remain after asynchronous writer flushing.

**Dependencies and integration points:** Extends `FileSystemMasterSyncMetadataTestBase`, uses PowerMock, Mockito spies, `UnderFileSystem` test hooks, journal protobuf entries, and master RPC contexts. It links `FileSystemJournalEntryMerger` behavior to real metadata sync.

**Risks:** Journal-entry count bounds are broad but still tied to implementation details such as access-time updates and directory journal sequence. Failure path for flat root expects a runtime exception, which can be sensitive to exception wrapping. Uses `Thread.sleep(1000)` to force timestamp differences.

**Test signals:** `SyncStatus.OK` for successful phases, `FAILED` or runtime on injected UFS failures, expected inode counts, directory loaded and file completed flags, appended journal counts within bounds, delete journal count equal to removed inodes, one flush count, and empty metadata-sync merger queues after sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataFlushJournalTest.java -->
