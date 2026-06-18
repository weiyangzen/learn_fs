# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatusIterator.java

## Purpose
`ReencryptionStatusIterator` adapts batched listing of encryption-zone re-encryption statuses into a retryable remote iterator.

## APIs and Control Flow
The constructor starts the cursor at `0L` and stores `ClientProtocol` plus tracer. `makeRequest(prevId)` opens a `listReencryptionStatus` trace scope and calls `namenode.listReencryptionStatus(prevId)`. `elementToPrevKey(entry)` returns the zone status ID.

## State, Dependencies, and Integration
State is inherited from `BatchedRemoteIterator`. It depends on `ZoneReencryptionStatus`, tracing, and `ClientProtocol`. It is used by admin/client code displaying re-encryption progress.

## Risks and Test Signals
Correctness depends on stable increasing zone IDs and NameNode-side batching. Tests should cover empty status lists, cursor advancement, tracing cleanup, failover retry behavior, and zones completing or being removed during iteration.
