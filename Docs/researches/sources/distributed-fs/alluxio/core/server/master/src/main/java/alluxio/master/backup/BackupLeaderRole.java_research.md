<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupLeaderRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupLeaderRole.java

## Purpose
Implements backup behavior while the master is primary. It exposes a backup messaging service to standby workers, initiates backups locally or by delegation, tracks progress, and aborts stale delegated backups.

## Important APIs, Types, And Functions
- `getRoleServices` registers `META_MASTER_BACKUP_MESSAGING_SERVICE`.
- `backup(BackupPRequest, StateLockOptions)` initiates synchronous or asynchronous backup.
- `getBackupStatus` queries the `BackupTracker`.
- `activateWorkerConnection`, `handleHandshakeMessage`, and `handleHeartbeatMessage` manage worker connections.
- `scheduleLocalBackup` locks master state and calls `takeBackup`.
- `scheduleRemoteBackup` suspends a worker, records journal sequence numbers, sends `BackupRequestMessage`, and starts abandon timeout.

## Control Flow
`backup` serializes initiation under `mBackupInitiateLock`, rejects concurrent backups, decides delegation based on HA/config/request options, initializes tracker state and hostname, then schedules local or remote work. Synchronous calls wait for completion; async calls return an initiating status immediately.

## State And Persistence Behavior
Leader state includes current tracker, worker connection set, hostname map, current remote connection, local backup future, heartbeat timeout, and last heartbeat time. Persistent backup files are produced through `AbstractBackupRole.takeBackup` either locally or on a worker.

## Dependencies And Integration Points
Integrates with `StateLockManager`, `JournalSystem` sequence numbers, gRPC messaging service handler, client context interceptor, `BackupTracker`, Alluxio HA configuration, and UFS backup writing.

## Risks And Edge Cases
No standby workers in HA mode causes delegation failure unless `allowLeader` is set. Worker connection loss during delegated backup marks the backup aborted. Heartbeat timeout is rescheduled on each heartbeat and fails stale backups.

## Test Signals
Signals include local backup success/failure, delegation selection, no-worker rejection, bypass delegation, async status behavior, worker loss aborts, heartbeat status propagation, and abandon timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupLeaderRole.java -->
