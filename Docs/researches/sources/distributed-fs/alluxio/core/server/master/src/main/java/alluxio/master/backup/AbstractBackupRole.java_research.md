<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/AbstractBackupRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/AbstractBackupRole.java

## Purpose
Shared implementation for backup leader and worker roles. It provides executor infrastructure, gRPC messaging serialization/context, backup status tracking, and the common local backup writer.

## Important APIs, Types, And Functions
- Constructor initializes cached executor, scheduled task executor, context dependencies, messaging context, transport timeout, and `BackupTracker`.
- `sendMessageBlocking` sends a Catalyst message over `GrpcMessagingConnection` and waits for acknowledgement.
- `takeBackup` creates the target backup file, streams master state through `BackupManager.backup`, and writes a `.complete` marker.
- `close` shuts down schedulers, messaging context, executors, and resets tracker.

## Control Flow
`takeBackup` resolves the backup parent directory from request or config, chooses root UFS or local UFS based on request options, ensures the directory exists, constructs a timestamped backup name, writes the backup, and deletes the incomplete file if writing fails.

## State And Persistence Behavior
Persistent output is a backup file plus `.complete` marker in UFS or local filesystem. In-memory state includes role closure, executors, messaging context, journal/backup managers, and current backup tracker.

## Dependencies And Integration Points
Integrates `CoreMasterContext`, `BackupManager`, `JournalSystem`, `UfsManager`, `UnderFileSystem`, Alluxio backup configuration, gRPC messaging transport, and Atomix Catalyst serialization.

## Risks And Edge Cases
Failure cleanup attempts to delete only the backup file, not the marker. Local filesystem requests require special UFS creation if root UFS is not local. Interrupted messaging is wrapped as runtime failure.

## Test Signals
Signals include successful backup file and marker creation, parent directory creation, local-filesystem option behavior, cleanup on backup write failure, and executor/context cleanup on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/AbstractBackupRole.java -->
