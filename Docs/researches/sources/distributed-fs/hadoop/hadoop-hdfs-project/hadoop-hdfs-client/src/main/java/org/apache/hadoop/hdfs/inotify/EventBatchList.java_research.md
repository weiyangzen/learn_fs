# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatchList.java

## Purpose
`EventBatchList` is the private HDFS client container for a page of inotify event batches plus transaction-id range metadata.

## Important APIs, types, and functions
The constructor stores a `List<EventBatch>`, `firstTxid`, `lastTxid`, and `syncTxid`. Getters expose the batch list and transaction ids.

## Control flow
There is no executable behavior beyond getters.

## State and persistence behavior
State is the referenced batch list and txid metadata. `firstTxid` identifies the first observed txid, `lastTxid` the last read txid, and `syncTxid` the latest NameNode synced txid. No local persistence occurs.

## Dependencies and integration points
It depends on `EventBatch` and is used by client inotify polling to determine event progress, lag, and whether gaps may have occurred after edit-log cleanup.

## Risks and test signals
Tests should cover empty batch pages, txid metadata consistency, lag calculations using `syncTxid`, and gap detection when `firstTxid` is higher than the requested next txid. The list reference is not copied.
