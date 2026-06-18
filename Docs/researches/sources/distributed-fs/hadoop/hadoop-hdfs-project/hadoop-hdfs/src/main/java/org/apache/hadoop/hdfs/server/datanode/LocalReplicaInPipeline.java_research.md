# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplicaInPipeline.java

Purpose: `LocalReplicaInPipeline` models a local replica currently being written, replicated, or copied. It extends `LocalReplica` and implements `ReplicaInPipeline`, tracking writer ownership, bytes acknowledged, bytes on disk, reserved space, and last checksum.

Important APIs: constructors create zero-length or existing pipeline replicas. State accessors include `getState`, `getVisibleLength`, `getBytesAcked`, `setBytesAcked`, `getBytesOnDisk`, reserved-space accessors, `setLastChecksumAndDataLen`, `getLastChecksumAndDataLen`, `waitForMinLength`, writer setters/interruption methods, `createStreams`, `createRestartMetaStream`, `moveReplicaFrom`, and `getReplicaInfo`.

Control flow: writes update `bytesOnDisk` and checksum under a lock and signal waiters. Acknowledged bytes release equivalent reserved volume space. `stopWriter` repeatedly interrupts and joins the current writer, handling races where the writer reference changes. `createStreams` opens metadata as a `RandomAccessFile`, validates checksum compatibility and existing lengths for append/recovery, positions block and checksum streams, and returns `ReplicaOutputStreams`.

State and persistence: in-memory state includes `bytesAcked`, `bytesOnDisk`, `lastChecksum`, `writer`, `bytesReserved`, and `originalBytesReserved`. Persistent effects include appending/truncating block and meta files, restart meta file creation, and moving finalized files into an RBW location. Reservation methods mutate volume reserved-space and locked-memory accounting.

Dependencies and integration points: it depends on `ReplicaInPipeline`, `ReplicaOutputStreams`, `BlockMetadataHeader`, `DataChecksum`, `FsVolumeSpi`, `FileIoProvider`, `IOUtils`, and DataNode logging. `BlockReceiver` and recovery code use it while receiving packets and transitioning replicas.

Risks: `getVisibleLength` returns `-1`, so callers must use pipeline-specific bytes when serving in-progress data. `setBytesAcked` assumes monotonic progress; lower values would release negative space. `createStreams` creates a raw `RandomAccessFile(blockFile, "rw")` just to obtain an FD before wrapping, so failure cleanup is important. `createRestartMetaStream` uses `File.pathSeparator` in the constructed filename, which is unusual for a path component and deserves compatibility coverage.

Test signals: verify reserved-space release, wait timeout/signal behavior, writer CAS and stop timeout, append checksum mismatch rejection, corrupt length detection, stream positioning, restart meta deletion/recreation, move rollback when block rename fails, unsupported recovery methods, and `releaseAllBytesReserved` interaction with locked memory.
