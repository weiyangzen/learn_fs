# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInotifyEventInputStream.java

## Purpose
`DFSInotifyEventInputStream` is the client-side stream for reading HDFS edit-log-derived inotify event batches from the NameNode. It is public but unstable and explicitly not intended to be shared by multiple threads.

## Important APIs, Types, and Functions
The stream holds a `ClientProtocol namenode`, current iterator of `EventBatch`, `lastReadTxid`, `syncTxid`, random backoff generator, and `Tracer`. Constructors either start from the NameNode current edit-log txid or from a caller-supplied last-read txid. Public methods are `poll()`, `poll(long, TimeUnit)`, `take()`, and `getTxidsBehindEstimate()`.

## Control Flow
`poll()` opens an `inotifyPoll` trace scope. If `lastReadTxid` is `-1`, it initializes from `namenode.getCurrentEditLogTxid()` and returns null. When the current batch iterator is empty, it calls `namenode.getEditsFromTxid(lastReadTxid + 1)`. If the NameNode returns edits, it updates `syncTxid`, replaces the iterator, advances `lastReadTxid` to the returned last txid, and throws `MissingEventsException` if the first returned txid does not immediately follow the previous one. It then returns the next converted event batch or null when no edit op converted to an event.

`poll(timeout)` repeatedly calls `poll()` with exponential sleep starting at 10 ms until an event arrives or the timeout expires. `take()` repeats indefinitely and sleeps for a randomized interval between `nextWaitMin` and `2 * nextWaitMin`, doubling up to a 60 second minimum window to avoid synchronized client polling.

## State and Persistence
The stream persists only its in-memory cursor (`lastReadTxid`) and lag estimate basis (`syncTxid`). The NameNode edit log is the durable source. `getTxidsBehindEstimate()` returns `-1` until at least one successful event fetch supplied a synced txid; otherwise it returns `syncTxid - lastReadTxid`.

## Dependencies and Integration Points
`DFSClient.getInotifyEventStream()` and `DistributedFileSystem.getInotifyEventStream()` construct this class. It depends on `ClientProtocol.getCurrentEditLogTxid` and `getEditsFromTxid`, inotify model classes `EventBatch`, `EventBatchList`, and `MissingEventsException`, and Hadoop tracing/time utilities.

## Risks
The class is not synchronized, so concurrent callers can corrupt iterator and txid state. Timeout waits can exceed the requested timeout by one NameNode RPC duration. If a client falls behind far enough that edit-log data is no longer available, `MissingEventsException` is expected and callers must decide how to resynchronize. The lag estimate is approximate and only updates after successful edit reads, so it should not be treated as exact monitoring data.

## Test Signals
`TestDFSInotifyEventInputStream` covers event delivery across filesystem operations, restart/upgrade cases use `TestDFSUpgradeFromImage`, and `TestDFSInotifyEventInputStreamKerberized` covers secure clusters. `TestDistributedFileSystem` verifies closed-client behavior for inotify stream creation. Important assertions include txid ordering, missing-event behavior, timeout/take behavior, and Kerberos access.
