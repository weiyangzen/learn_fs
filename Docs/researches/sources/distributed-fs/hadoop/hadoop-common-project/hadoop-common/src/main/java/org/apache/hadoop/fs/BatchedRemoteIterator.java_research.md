## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchedRemoteIterator.java

Purpose: provides a generic `RemoteIterator` implementation that pages through remote results using a previous-key marker.

Important APIs and types: nested `BatchedEntries<E>` exposes `get`, `size`, and `hasMore`; `BatchedListEntries<E>` wraps a `List<E>` plus a continuation flag; subclasses implement `makeRequest(K prevKey)` and `elementToPrevKey(E element)`.

Control flow: first `hasNext` or `next` triggers `makeRequest(prevKey)`. When the current batch is exhausted, `hasMore=false` ends iteration, while `hasMore=true` requests another batch using the last returned element's key. Empty returned batches are treated as end-of-data by setting `entries` to null.

State and persistence behavior: holds only in-memory iterator cursor state: previous key, current entries, and current index. It performs no persistence.

Dependencies and integration points: intended for HDFS and object-store listing APIs that use marker-based pagination, while exposing the standard Hadoop `RemoteIterator` contract.

Risks: if a service returns an empty batch with `hasMore=true`, iteration terminates early. If `elementToPrevKey` is unstable or non-monotonic, callers can skip or repeat entries. The class is not thread-safe.

Test signals: cover initial request, multi-page traversal, empty first page, exact-boundary pages, `next()` after exhaustion, and marker progression from returned entries.
