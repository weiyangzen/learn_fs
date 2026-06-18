# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/CorruptFileBlockIterator.java

## Purpose
`CorruptFileBlockIterator` adapts `DFSClient.listCorruptFileBlocks` into a `RemoteIterator<Path>` for `DistributedFileSystem` and `Hdfs` callers.

## Important APIs, types, and functions
The constructor stores the `DFSClient`, converts the requested `Path` to a URI path string, and preloads the first result. `hasNext()` checks whether `nextPath` is populated. `next()` returns the current path and advances the iterator or throws `NoSuchElementException` when exhausted. `getCallsMade()` exposes the number of DFSClient RPC calls for debugging/tests.

## Control flow
`loadNext()` fetches a new `CorruptFileBlocks` batch when no batch exists or the current batch has been consumed. It updates `files`, `cookie`, `fileIdx`, and `callsMade`, then either converts the next string to a `Path` or marks exhaustion with `nextPath = null`. The cookie is passed back to the NameNode for paginated continuation.

## State and persistence behavior
State is in-memory iterator state: current file-name array, index, continuation cookie, next path, and call count. It persists nothing locally.

## Dependencies and integration points
It depends on `DFSClient`, `CorruptFileBlocks`, Hadoop `Path`, and `RemoteIterator`. It is part of the client-side public filesystem listing path for corrupt block reports.

## Risks and test signals
Tests should cover empty first response, multiple batches, cookie continuation, `NoSuchElementException` after exhaustion, path string/URI conversion, and call-count behavior. A risk is that an empty response is interpreted as completion; the NameNode contract must guarantee that no later batch is reachable after an empty file list.
