# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LastBlockWithStatus.java

## Purpose
`LastBlockWithStatus` is the append-response wrapper containing the last partial `LocatedBlock` and the file status returned by `ClientProtocol.append`.

## APIs and Behavior
The constructor stores final `lastBlock` and `fileStatus` references. `getLastBlock()` and `getFileStatus()` expose them.

## State, Dependencies, and Integration
There is no logic or persistence. It integrates with append setup, allowing clients to resume writing from the last block while also refreshing status metadata.

## Risks and Test Signals
The wrapper does not validate null values, which may be valid for some server capabilities but should be explicit in callers. Tests should cover append responses with and without a partial last block/status, and downstream client behavior when either field is null.
