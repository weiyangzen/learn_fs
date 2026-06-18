# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveIterator.java

## Purpose
`CacheDirectiveIterator` is a `BatchedRemoteIterator` over HDFS cache directives, with tracing and a compatibility fallback for older NameNodes that cannot filter by directive id.

## Important APIs, types, and functions
The constructor takes a `ClientProtocol`, `CacheDirectiveInfo` filter, and `Tracer`, starting iteration at previous id `0L`. `makeRequest(Long)` calls `namenode.listCacheDirectives`. `elementToPrevKey` returns the entry id for pagination. `removeIdFromFilter` clears the id from a filter. The nested `SingleEntry` wraps exactly one matching entry as a `BatchedEntries` result.

## Control flow
Each batch request runs inside a trace scope named `listCacheDirectives`. If the server throws an `IOException` containing `"Filtering by ID is unsupported"`, the iterator removes the id filter, requests a page starting at `id - 1`, scans for the requested id, and returns a single-entry result. If the id is not found, it throws a `RemoteException` wrapping `InvalidRequestException`.

## State and persistence behavior
State is the current mutable filter, NameNode proxy, and tracer. The filter may be changed after compatibility fallback. No local persistence occurs.

## Dependencies and integration points
It depends on `BatchedRemoteIterator`, `ClientProtocol`, tracing, `RemoteException`, `InvalidRequestException`, and `CacheDirectiveEntry`. It is used by HDFS cache directive list APIs and must handle failover/retry semantics inherited from `BatchedRemoteIterator`.

## Risks and test signals
Tests should cover normal pagination, trace-scope creation, prev-key extraction, compatibility fallback with matching id, fallback with missing id, brittle ordering assumption around `id - 1`, exception propagation for unrelated IO failures, and null-entry precondition behavior.
