<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRequestMessage.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRequestMessage.java

## Purpose
Serializable leader-to-worker message instructing a standby master to take a delegated backup at a consistent journal point.

## Important APIs, Types, And Functions
- Stores backup UUID, client `BackupPRequest`, and a map of journal names to target sequence numbers.
- `writeObject` serializes UUID string, protobuf request bytes, and journal sequence map.
- `readObject` reconstructs request bytes with `BackupPRequest.parseFrom` and rebuilds the sequence map.

## Control Flow
The leader sends this after successfully suspending a standby and collecting current journal sequence numbers under the state lock. The worker uses the sequence map to catch up before taking the backup.

## State And Persistence Behavior
The message carries transient protocol state. Its journal sequence map is the consistency boundary for delegated backup, while actual persistence happens when the worker writes the backup file.

## Dependencies And Integration Points
Depends on gRPC `BackupPRequest`, Atomix Catalyst serialization, protobuf parsing, Java UUID/map types, and Guava `MoreObjects`. Consumed by `BackupWorkerRole.handleRequestMessage`.

## Risks And Edge Cases
Deserialization failure for the request becomes runtime failure. Map iteration order is not preserved or required, but every journal sequence key must be present for correct catchup.

## Test Signals
Signals include UUID/request/sequence serialization round-trip and worker catchup behavior using the received sequence map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupRequestMessage.java -->
