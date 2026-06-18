<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupOps.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupOps.java

## Purpose
Defines the public backup operations supported by backup roles: start a backup and query backup status.

## Important APIs, Types, And Functions
- `backup(BackupPRequest, StateLockOptions)` starts a backup and returns status, with async behavior controlled by request options.
- `getBackupStatus(BackupStatusPRequest)` retrieves the latest or identified backup status.

## Control Flow
This interface does not implement flow, but its contract documents two important behaviors: async requests return once initiated, and HA leaders without standby workers reject delegated backup unless the request allows leader backup.

## State And Persistence Behavior
Implementations persist backup files through role-specific execution and expose status through `BackupStatus`. The interface itself is stateless.

## Dependencies And Integration Points
Depends on gRPC backup request/status types, `StateLockOptions`, Alluxio exceptions, and wire `BackupStatus`. Implemented by `BackupLeaderRole` and rejected by `BackupWorkerRole` for RPC serving.

## Risks And Edge Cases
Callers must understand async status polling and HA delegation semantics. State lock options affect how strongly metadata changes are paused during backup.

## Test Signals
Tests should verify implementations honor sync/async behavior, exception semantics, and status lookup contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupOps.java -->
