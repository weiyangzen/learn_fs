# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZoneIterator.java

## Purpose
`EncryptionZoneIterator` adapts the batched NameNode encryption-zone listing RPC into a `BatchedRemoteIterator<Long, EncryptionZone>` that supports retries across failover.

## APIs and Control Flow
The constructor starts the cursor at `0L` and stores `ClientProtocol` plus a `Tracer`. `makeRequest(prevId)` opens a tracing scope named `listEncryptionZones` and calls `namenode.listEncryptionZones(prevId)`. `elementToPrevKey(entry)` returns `entry.getId()` for the next cursor.

## State, Dependencies, and Integration
State is only the remote iterator cursor inherited from `BatchedRemoteIterator`. It integrates with NameNode `ClientProtocol` batching, tracing, and `EncryptionZone` IDs.

## Risks and Test Signals
Correctness depends on stable monotonic zone IDs from the NameNode. Tests should cover empty first batch, multi-batch cursor advancement, retry/failover behavior, trace-scope closure, and zones created/deleted during iteration.
