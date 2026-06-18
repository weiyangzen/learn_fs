# sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache_test.go

## Purpose

`persisted_log_cache_test.go` validates the metadata persisted-log cache, chunk decoder, and `LogFileIterator` integration paths. It uses stub loaders to avoid real volume-server reads.

## Important APIs, Types, and Functions

Helpers include `logEntriesAt`, `encodeLogRecords`, `stubChunkLoader`, `logFileEntry`, and `collectTs`. Tests cover `persistedLogCache.getOrLoad`, `decodeLogRecords`, `newLogFileIterator`, cache eviction, stream fallback, and load error propagation.

## Control Flow

Cache tests assert first-load/second-hit behavior, uncacheable reloads, singleflight across 20 goroutines, and LRU/idle eviction. Decode tests build size-prefixed protobuf buffers and truncate or corrupt them to expect `errLogChunkIncomplete`. Iterator tests stub chunk loading, filter timestamps, skip cold chunks based on flush time, share decoded chunks across replays, fall back to whole-file streaming when records span chunks, skip already-yielded records after fallback, and surface loader errors.

## State and Persistence Behavior

All cache state is in-memory. Loader functions are temporarily swapped via package variables and restored with `t.Cleanup`. Encoded log file entries simulate persisted chunks without touching actual filer storage.

## Dependencies and Integration Points

The tests depend on protobuf marshal/unmarshal, the filer log iterator from `filer_notify_read.go`, and `wdclient` type signatures for stubbed loaders. They validate subscriber replay behavior around persisted log chunks.

## Risks and Edge Cases

Global function swaps would be unsafe under parallel tests; these tests do not call `t.Parallel`. The cache constructor starts background eviction goroutines, so many tests create goroutines that live until process exit. Stringified slice comparisons are simple but sufficient for timestamp order.

## Test Signals

Strong signals include exactly one coalesced load, no caching for uncacheable results, correct timestamp filtering, no duplicate records after stream fallback, and correct rejection of implausible zero/non-increasing timestamp records.
