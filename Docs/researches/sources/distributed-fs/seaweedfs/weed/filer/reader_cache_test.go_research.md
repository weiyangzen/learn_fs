# sources/distributed-fs/seaweedfs/weed/filer/reader_cache_test.go

## Purpose

`reader_cache_test.go` exercises `ReaderCache` and `SingleChunkCacher` concurrency behavior without requiring real volume-server HTTP fetches. It was read as a complete 545-line file.

## Important APIs, Types, and Functions

`mockChunkCacheForReaderCache` implements the chunk cache methods needed by `ReaderCache`: `ReadChunkAt`, `SetChunk`, `IsInCache`, and max-cache-size reporting. Tests include `TestReaderCacheContextCancellation`, `TestReaderCacheFallbackToChunkCache`, `TestReaderCacheMultipleReadersWaitForSameChunk`, `TestReaderCachePartialRead`, `TestReaderCacheCleanup`, `TestSingleChunkCacherLookupError`, `TestSingleChunkCacherContextCancellationDuringLookup`, `TestReaderCacheDownloaderDedup`, and `TestSingleChunkCacherOneReaderCancelsOthersContinue`.

## Control Flow

Most tests pre-populate the mock cache to avoid HTTP, then call `ReadChunkAt` concurrently. The more direct `SingleChunkCacher` tests provide blocking lookup functions and use channels to force reads to wait, cancel, or resume.

## State and Persistence Behavior

State is in-memory test data plus atomic hit/lookup counters. The tests verify that cached byte slices are reused, hit counts increase, and concurrent reader goroutines complete without hanging.

## Dependencies and Integration Points

The file depends on `testing`, `context`, `sync`, `atomic`, and the production reader cache API. It validates the contract expected by streaming code that may have multiple readers waiting on the same fileId.

## Risks and Edge Cases

The tests target regressions where a request context cancellation aborts a shared download, `done` is not closed, duplicate network lookups are started for one fileId, or offset reads return zero bytes without falling back.

## Test Signals

This file is itself the primary test signal for `reader_cache.go`; it is especially strong for concurrency ordering and weak for actual HTTP/decryption/gzip fetch success because those are intentionally not mocked end-to-end.
