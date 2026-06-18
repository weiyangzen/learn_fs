<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHeartbeatMessage.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHeartbeatMessage.java

## Purpose
Serializable control message used by backup workers to report current backup status to the leader.

## Important APIs, Types, And Functions
- Constructors support empty Catalyst deserialization and optional `BackupStatus` payload.
- `getBackupStatus` returns nullable status.
- `writeObject` writes a presence boolean and, when present, serialized `BackupPStatus`.
- `readObject` reconstructs `BackupStatus` from protobuf bytes.

## Control Flow
Worker heartbeat tasks periodically send this message. The leader handler updates `BackupTracker` and adjusts abandon timeout when a status is present. Null status is allowed and effectively acts as an acknowledgement without status update.

## State And Persistence Behavior
State is transient. It carries backup id, state, entry count, URI/error fields embedded in `BackupStatus` serialization but does not persist by itself.

## Dependencies And Integration Points
Depends on Alluxio wire `BackupStatus`, gRPC `BackupPStatus`, Atomix Catalyst serialization, and Guava `MoreObjects`. It is central to delegated backup progress propagation.

## Risks And Edge Cases
Malformed protobuf bytes become runtime deserialization failures. The nullable design requires handlers to avoid assuming status exists.

## Test Signals
Tests should cover null and non-null serialization, status field round-trips, and leader tracker updates from heartbeat messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHeartbeatMessage.java -->
