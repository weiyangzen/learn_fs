<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHandshakeMessage.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHandshakeMessage.java

## Purpose
Serializable control message used by a backup worker to introduce itself to the backup leader and associate a hostname with the gRPC messaging connection.

## Important APIs, Types, And Functions
- Constructors support Catalyst-required empty creation and hostname creation.
- `getBackupWorkerHostname` returns the worker hostname.
- `setConnection` and `getConnection` attach the inbound `GrpcMessagingConnection` after receipt; the connection is not serialized.
- `writeObject`/`readObject` serialize only the hostname string.

## Control Flow
Workers send this message after establishing a leader connection. The leader handler sets the connection and records hostname by connection in its worker maps.

## State And Persistence Behavior
State is transient message payload and a non-serialized connection reference. No durable persistence is involved.

## Dependencies And Integration Points
Depends on `GrpcMessagingConnection`, Atomix Catalyst serialization, and Guava `MoreObjects`. It is registered by backup messaging contexts in `AbstractBackupRole`.

## Risks And Edge Cases
The connection field is meaningful only after leader-side handler injection; deserialized messages initially have no connection. Null hostname from empty constructor should not be used as a real handshake.

## Test Signals
Signals include correct hostname serialization/deserialization, connection attachment on receipt, and leader worker-map population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/backup/BackupHandshakeMessage.java -->
