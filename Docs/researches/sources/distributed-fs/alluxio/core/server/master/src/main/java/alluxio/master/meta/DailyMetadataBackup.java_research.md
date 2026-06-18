# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DailyMetadataBackup.java

## Purpose
`DailyMetadataBackup` schedules automatic daily backups of primary master metadata at a configured UTC time and prunes old backup files according to retention settings.

## Important APIs, types, and functions
The constructor captures `MetaMaster`, scheduler, `UfsManager`, backup directory, retained-file count, and whether root UFS is local. `start()` schedules `dailyBackup()` at fixed daily rate. `dailyBackup()` invokes `MetaMaster.backup` with `StateLockOptions.defaultsForDailyBackup()` and then `deleteStaleBackups()`. `stop()` cancels the scheduled future and shuts down the executor.

## Control flow
`getTimeToNextBackup()` parses `MASTER_DAILY_BACKUP_TIME` as UTC `H:mm`, schedules today if still future, otherwise tomorrow. Backup request sets target directory and local-filesystem option based on root UFS type. Retention lists backup dir, filters files matching `BackupManager.BACKUP_FILE_PATTERN`, sorts by timestamp from filename, and deletes oldest beyond the configured retention count.

## State and persistence behavior
The class owns scheduling state (`ScheduledFuture`) and writes backup files through meta master backup machinery. It deletes stale persisted backup files from the configured backup directory.

## Dependencies and integration points
It depends on `MetaMaster.backup`, `UfsManager`, `UnderFileSystem`, backup manager filename pattern, Alluxio configuration, path utilities, and scheduled executor services. `DefaultMetaMaster` starts it only on primary when daily backup is enabled.

## Risks
Retention cleanup assumes backup filenames contain sortable timestamps and uses a `TreeMap<Instant, String>` comparator that treats equal instants as equal keys, potentially dropping duplicates. `ufs.listStatus(mBackupDir)` may return null or throw depending on UFS behavior. Backup and cleanup catch `Throwable`, log, and continue, so failures rely on log monitoring.

## Test signals
Tests should cover UTC schedule calculation, local versus non-local backup option, successful backup logging, backup failure isolation, retention deletion count/order, nonmatching files preserved, duplicate timestamp behavior, and stop cancellation/shutdown timeout.
