<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupTracker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupTracker.java

## Purpose
Tracks current and recently finished backup status, entry counts, completion signaling, and failure propagation.

## Important APIs, Types, And Functions
- `reset` initializes `BackupState.None`, counter, and completion future, failing any in-progress backup.
- `getCurrentStatus` returns a defensive copy with current entry count.
- `getStatus(UUID)` returns current matching status, finished status, or `None`.
- `update`, `updateHostname`, `updateBackupUri`, `updateState`, and `updateError` mutate status.
- `waitUntilFinished` blocks until completed or failed.
- `inProgress` checks state and completion future.

## Control Flow
Status updates call `signalIfFinished`. Completed backups set the completion future successfully; failed backups set it exceptionally. Finished statuses are stored by UUID for later lookup. Reset uses a fair lock to serialize replacement.

## State And Persistence Behavior
State is in-memory only: current `BackupStatus`, `SettableFuture`, `AtomicLong` entry counter, fair lock, and concurrent finished-backups map. It does not persist historical statuses beyond process memory.

## Dependencies And Integration Points
Depends on Alluxio backup states/status, exceptions, Guava `SettableFuture`, and `LockResource`. Used by both backup leader and worker roles.

## Risks And Edge Cases
Some update methods mutate `mBackupStatus` without acquiring `mStatusLock`, so thread-safety relies on external sequencing in several paths. Calling `signalIfFinished` repeatedly could attempt to complete an already completed future.

## Test Signals
Tests should cover reset during in-progress backup, completed and failed signaling, timed wait behavior, status copying with entry count, finished status lookup, and concurrent update safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupTracker.java -->
