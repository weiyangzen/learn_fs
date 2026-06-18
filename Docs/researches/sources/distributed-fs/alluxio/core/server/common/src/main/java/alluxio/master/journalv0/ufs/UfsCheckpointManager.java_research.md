# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsCheckpointManager.java

## Purpose
`UfsCheckpointManager` manages crash-safe updates to a legacy UFS journal checkpoint. It coordinates temporary checkpoint, backup checkpoint, completed-log cleanup, and recovery from interrupted rename sequences.

## Important APIs, Types, and Functions
The main methods are `recover()` and `update(URI)`. State includes `mUfs`, `mCheckpoint`, `mBackupCheckpoint`, `mTempBackupCheckpoint`, and a `UfsJournalWriter` used to delete completed logs. It uses `UnderFileSystemUtils.deleteFileIfExists()` and UFS `renameFile()`.

## Control Flow, State, and Persistence
`update()` deletes stale backup files, renames the existing checkpoint to a temporary backup and then to a stable backup, renames the new temporary checkpoint into `checkpoint.data`, deletes completed logs because the new checkpoint includes them, and removes the backup. `recover()` inspects the presence of checkpoint, backup, and temp backup files, restores `checkpoint.data` from the temp backup if needed, either rolls back from backup or finalizes cleanup after a completed rename, and asserts that all three files never coexist.

## Dependencies and Integration Points
It depends on `UnderFileSystem`, `UfsJournalWriter`, Guava `Preconditions`, URI construction, and UFS file operations. It is invoked by `UfsJournalWriter` before creating a checkpoint stream and when closing a completed checkpoint.

## Risks and Test Signals
Risks include UFS rename implementations that behave as copy-plus-delete, path handling via `location.getPath()` for new checkpoints, runtime exception wrapping of I/O failures, and log deletion before backup cleanup. Signals are crash-recovery matrix tests for every rename step, object-store rename behavior, completed-log deletion after checkpoint success, and idempotent recovery.
