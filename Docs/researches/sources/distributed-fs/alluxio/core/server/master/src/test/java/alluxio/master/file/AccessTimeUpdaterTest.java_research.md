<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/AccessTimeUpdaterTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/AccessTimeUpdaterTest.java

**Purpose:** Tests `AccessTimeUpdater`, which updates inode access time immediately or asynchronously while respecting access-time precision and journal flush lifecycle.

**Important APIs/types/functions:** Uses `AccessTimeUpdater.updateAccessTime`, `start`, scheduler-driven flush, `InodeTree.createPath`, `LockedInodePath`, `JournalContext.append`, `FileSystemMaster.createJournalContext`, `ControllableScheduler.jumpAndExecute`, and journal `UpdateInode` entries.

**Control flow:** The fixture constructs a real `InodeTree`, `InodeStore`, `BlockMaster`, UFS-backed journal system, root inode, and mock `FileSystemMaster`. `updateAccessTimeImmediately` uses zero async interval and precision to verify immediate inode mutation and journal append. `updateAccessTimeAsync` verifies inode mutation happens immediately while journal append waits for flush interval. `updateAccessTimePrecision` and `updateAccessTimePrecisionAsync` verify small timestamp deltas are suppressed and large deltas are applied. `updateAccessTimeAsyncOnShutdown` stops the journal system and verifies pending async access time is flushed.

**State and persistence behavior:** Tests both inode-store state (`lastAccessTimeMs`) and journal persistence behavior (`UpdateInode` append). Async mode accumulates pending access-time updates and flushes them later through a master-created journal context or shutdown hook.

**Dependencies and integration points:** Integrates `JournalSystem`, `JournalTestUtils`, `NoopJournalContext`, `MountTable`, `InodeLockManager`, `InodeDirectoryIdGenerator`, permission configuration, Mockito captors, and a controllable executor/scheduler. This is a high-fidelity unit/integration test for metadata mutation and journaling.

**Risks:** Uses current wall-clock values for timestamps, so very small time assumptions could be sensitive if clock behavior changes. The test relies on mocked journal context identity (`when(journalContext.get()).thenReturn(journalContext)`) and on manual scheduler execution matching the updater's scheduled tasks.

**Test signals:** Captured journal entries must have `UpdateInode`, correct inode id, and expected access time. Inode store values must update only when precision allows, and mocked journal context must not receive early appends in async scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/AccessTimeUpdaterTest.java -->
