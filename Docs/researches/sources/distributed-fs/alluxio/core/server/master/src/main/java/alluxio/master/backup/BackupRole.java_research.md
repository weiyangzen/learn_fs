<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRole.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRole.java

## Purpose
Combines backup operation handling with role-specific gRPC service exposure and closeable lifecycle.

## Important APIs, Types, And Functions
- Extends `BackupOps` and `Closeable`.
- `getRoleServices()` returns a map from `ServiceType` to `GrpcService` for services that should be registered while the role is active.

## Control Flow
Implementations choose whether they serve RPCs. The leader role exposes backup messaging service and handles backup RPCs; the worker role exposes no services and rejects direct backup/status RPCs.

## State And Persistence Behavior
The interface is stateless. Implementations manage backup state, messaging connections, executors, and backup file persistence.

## Dependencies And Integration Points
Depends on Alluxio `GrpcService` and `ServiceType`. It is consumed by master role management code to attach backup services appropriate to primary/standby state.

## Risks And Edge Cases
Service maps must be updated when roles change, otherwise stale leader/worker services could remain exposed. Close behavior is part of the contract through `Closeable`.

## Test Signals
Tests should verify leader and worker service maps match role expectations and resources close cleanly on role transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRole.java -->
