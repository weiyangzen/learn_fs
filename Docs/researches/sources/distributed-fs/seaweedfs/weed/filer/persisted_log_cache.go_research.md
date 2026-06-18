# sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache.go

## Purpose

`persisted_log_cache.go` caches decoded metadata log chunks used by SubscribeMetadata replay. It reduces repeated volume-server fetch and protobuf decode cost when multiple subscribers replay the same flushed metadata log chunks.

## Important APIs, Types, and Functions

`persistedLogCache` is an LRU cache keyed by chunk file ID. It uses a mutex, list/index map, current byte estimate, max bytes, `singleflight.Group`, and weighted semaphore. `getOrLoad`, `lookup`, `store`, `evictIdle`, `loadGuarded`, `estimateEntriesBytes`, `loadLogFileEntries`, and `decodeLogRecords` are the core functions. `logCacheItem` stores decoded immutable `LogEntry` slices.

## Control Flow

`getOrLoad` checks the cache, coalesces concurrent misses by file ID, limits in-flight load bytes with a semaphore, calls a loader, and only caches successful cacheable decodes. A background goroutine evicts entries idle for five minutes. `loadLogFileEntries` fetches a full chunk through volume lookup and decodes it. `decodeLogRecords` parses 4-byte length-prefixed protobuf `LogEntry` records, requiring positive size, bounded size, positive strictly increasing timestamps, and complete record boundaries.

## State and Persistence Behavior

The cache is process-local and bounded by byte estimate, defaulting to 256 MiB retained and 128 MiB concurrent load budget. It does not persist entries; source-of-truth logs remain persisted filer log chunks. Cached slices are shared read-only.

## Dependencies and Integration Points

The file depends on SeaweedFS chunk fetch helpers, `wdclient.MasterClient`, protobuf unmarshalling, `singleflight`, semaphores, and the `LogFileIterator` in `filer_notify_read.go`, which switches to stream fallback when chunks do not decode standalone.

## Risks and Edge Cases

Corrupt or partial chunks must not be cached because later complete reads may succeed. `proto.Unmarshal` can accept arbitrary bytes, so timestamp/order invariants are used as additional alignment checks. The background eviction goroutine lives for process lifetime. Byte estimates are conservative but not exact. Load weight is clamped so oversized chunks cannot deadlock on the semaphore.

## Test Signals

Tests should cover cache hits/misses, uncacheable results, singleflight coalescing, LRU budget eviction, idle eviction, clean/incomplete/corrupt decode, oversized load weight clamping, chunk filtering by timestamp, and stream fallback when records span chunk boundaries.
