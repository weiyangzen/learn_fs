# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatch.java

## Purpose
`EventBatch` groups all inotify `Event` objects that occurred under the same NameNode transaction ID.

## Important APIs, types, and functions
The constructor accepts a `txid` and `Event[]`. `getTxid()` returns the transaction id, and `getEvents()` returns the event array.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
The class stores the event array reference directly and has no persistence. It is a client-side transport/value object.

## Dependencies and integration points
It depends on `Event` and classification annotations. It is contained in `EventBatchList` and delivered by the inotify stream to clients.

## Risks and test signals
Tests should verify txid/event preservation, empty event arrays, and caller expectations around array mutability. Inotify ordering relies on batches being processed by txid.
