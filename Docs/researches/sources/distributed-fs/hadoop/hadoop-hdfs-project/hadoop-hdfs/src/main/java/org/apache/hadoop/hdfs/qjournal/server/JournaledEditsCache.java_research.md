# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournaledEditsCache.java

## Purpose
`JournaledEditsCache` is an in-memory serialized edit cache used by `Journal#getJournaledEdits(long, int)` when in-progress tailing is enabled. It lets clients fetch recent contiguous journaled edits without reading the edit log from disk.

## Important APIs and types
The main methods are `storeEdits(byte[] inputData, long newStartTxn, long newEndTxn, int newLayoutVersion)` and `retrieveEdits(long requestedStartTxn, int maxTxns, List<ByteBuffer> outputBuffers)`. The cache stores a `TreeMap<Long, byte[]>` of batch start transaction ID to serialized edits. `CacheMissException` reports the amount by which the cache missed.

## Control flow
Construction validates the configured cache-size fraction, computes byte capacity from explicit size or JVM heap fraction, initializes a fair read/write lock, and starts empty. `storeEdits` rejects malformed transaction ranges, updates the edit-log layout header when the layout version changes, clears the cache when incoming batches are noncontiguous, evicts oldest batches until the new batch fits, and drops the whole cache if a single batch exceeds capacity. `retrieveEdits` validates that the requested start is cached, appends the serialized header, selects buffers from the floor entry through enough subsequent batches, then trims the first and last buffers by scanning serialized edit operations for exact transaction boundaries.

## State and persistence
All state is memory-only: layout version, serialized header, contiguous batch map, lowest/highest transaction IDs, initial transaction ID since reset, and total byte size. It persists nothing to disk and can be safely treated as an optimization. Locks protect map and metadata, while byte arrays are treated as immutable after insertion.

## Dependencies and integration points
It integrates with `Journal` write and tail-edit RPC paths, `EditLogFileOutputStream.writeHeader`, `FSEditLogOp.Reader`, `FSEditLogLoader.PositionTrackingInputStream`, `JournalMetrics` through cache-miss accounting outside this class, and DFS cache-size configuration keys.

## Risks and edge cases
`retrieveEdits` assumes there is at least one edit buffer after a successful nonempty range validation; callers requesting available but zero `maxTxns` would be risky if not guarded upstream. Transaction boundary trimming scans edit serialization, so corrupt cached bytes or incorrect layout versions surface as `IOException`. Noncontiguous writes reset the cache rather than representing holes, which is appropriate for tailing but can increase cache misses after recovery paths.

## Test signals
Tests should cover capacity validation, layout-version transitions, contiguous and noncontiguous `storeEdits`, over-capacity eviction, oversized single batch clearing, exact trimming across batch boundaries, empty/high-start responses, low-start cache misses with miss amounts, and concurrent reader/writer behavior.
