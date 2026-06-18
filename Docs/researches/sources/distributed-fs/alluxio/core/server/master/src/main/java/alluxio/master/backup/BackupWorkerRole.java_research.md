<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupWorkerRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupWorkerRole.java

## Purpose
Implements backup behavior while a master is standby. It maintains a connection to the primary backup leader, handles suspend and backup request messages, catches up journals, writes delegated backups, sends progress heartbeats, and resumes journals.

## Important APIs, Types, And Functions
- Constructor reads heartbeat/connect/suspend timeout settings and starts leader connection maintenance.
- `getRoleServices` returns no services; direct `backup` and `getBackupStatus` throw because workers do not serve backup RPCs.
- `handleSuspendJournalsMessage` suspends journal application and schedules timeout resume.
- `handleRequestMessage` initializes tracker, starts heartbeat, catches up to requested journal sequences, takes backup, and resumes journals.
- `startHeartbeatThread` periodically sends `BackupHeartbeatMessage`.
- `activateLeaderConnection` registers handlers and sends `BackupHandshakeMessage`.
- `establishConnectionToLeader` repeatedly discovers and connects to the primary.

## Control Flow
The worker continuously retries leader discovery until connected. On suspend, it pauses journal application. On request, it cancels the suspend timeout, transitions tracker through initiating/transitioning/running/completed or failed, and always resumes journals in finally. If leader connection closes, active backup is canceled and connection establishment restarts.

## State And Persistence Behavior
Worker state includes leader connection/listener, backup future, heartbeat future, timeout task, tracker, and suspended journal state. Persistent output is the delegated backup file created by `takeBackup`.

## Dependencies And Integration Points
Integrates `MasterInquireClient`, `GrpcMessagingClient`, `JournalSystem.suspend/catchup/resume`, `CatchupFuture`, backup messages, Alluxio retry policies, and network address utilities.

## Risks And Edge Cases
Failure to resume journals is fatal. A suspend not followed by request times out and resumes journals. If catchup exceeds 30 seconds, backup fails. Leader loss cancels active backup and resets tracker.

## Test Signals
Signals include leader connection retry, handshake delivery, suspend timeout resume, delegated backup success, journal catchup timeout failure, heartbeat propagation, interruption handling, and fatal resume failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupWorkerRole.java -->
