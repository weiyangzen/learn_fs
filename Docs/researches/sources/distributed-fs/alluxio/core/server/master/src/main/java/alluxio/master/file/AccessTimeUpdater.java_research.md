# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/AccessTimeUpdater.java

## Purpose
`AccessTimeUpdater` batches or synchronously journals inode last-access-time updates for `DefaultFileSystemMaster`. It reduces journal traffic by applying precision thresholds and optional scheduled flushing.

## Important APIs and Types
- Package-private final class implementing `JournalSink`.
- Constructors wire `FileSystemMaster`, `InodeTree`, `JournalSystem`, flush interval, update precision, and shutdown timeout.
- Lifecycle: `start`, testing `start(ScheduledExecutorService)`, `beforeShutdown`, `stop`.
- Main API: `updateAccessTime(JournalContext, Inode, opTimeMs)`.
- Internal batching: `scheduleJournalUpdate`, `flushScheduledUpdates`, `flushUpdates`.

## Control Flow
Construction registers the updater as a journal sink for the file-system master. `start` creates a single-thread scheduled executor when the flush interval is positive; otherwise access-time updates journal synchronously. `updateAccessTime` ignores updates within the configured precision window. For accepted updates, it takes the inode update lock. In async mode, it updates inode metadata without journaling, stores the latest time per inode in a concurrent map, and schedules one delayed flush if none is pending. In sync mode, it calls `InodeTree.updateInode` with the caller's journal context.

`flushUpdates` creates a file-system master journal context, drains queued inode/time pairs by removing entries while iterating, and appends `UpdateInodeEntry` journal entries. `beforeShutdown` flushes pending updates, and `stop` shuts down the executor.

## State and Persistence Behavior
The durable state is journaled `UpdateInodeEntry` records. Async mode creates a window where inode memory state has been updated but journal records are pending; `beforeShutdown` reduces loss on orderly shutdown. The concurrent map coalesces repeated updates by inode ID so only the latest queued time is flushed.

## Dependencies and Integration Points
It depends on `FileSystemMaster`, `InodeTree`, inode lock manager, `JournalSystem` and `JournalSink`, `JournalContext`, file journal proto entries, configuration keys, and executor utilities. `DefaultFileSystemMaster` constructs, starts/stops, and calls it during access-time updates.

## Risks and Edge Cases
The class is marked not thread-safe but uses concurrent structures for the update queue. If `flushUpdates` catches `UnavailableException`, removed entries are already dropped, so those access-time journal updates can be lost. Async inode updates before journal flush can be lost on abrupt master failure. The precision check reads the inode time before acquiring the update lock, so concurrent updates can affect whether a later update is skipped. If executor shutdown races with scheduling, flush timing depends on lifecycle ordering.

## Test Signals
`AccessTimeUpdaterTest` covers synchronous and asynchronous update paths, precision filtering, coalescing/scheduled flush behavior, and shutdown flushing with a controllable scheduler.
