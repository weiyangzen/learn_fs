# sources/distributed-fs/seaweedfs/weed/filer/stream_benchmark_test.go

## Purpose

`stream_benchmark_test.go` benchmarks sequential streaming versus pipe-based prefetch streaming under synthetic latency. It was read as a complete 317-line file.

## Important APIs, Types, and Functions

`TestMain` initializes the global HTTP client. Helpers include `mockMasterClientForBenchmark`, `createMockVolumeServer`, `benchmarkConfig`, `setupBenchmark`, `runSequentialBenchmark`, and `runPrefetchBenchmark`. Benchmarks are `BenchmarkStreamSequential`, `BenchmarkStreamSequentialVerify`, `BenchmarkStreamPrefetch`, and `BenchmarkStreamPrefetchVerify`.

## Control Flow

The benchmark creates random chunk data, serves it from `httptest.Server` with optional request latency and range support, maps fileIds to URLs, and repeatedly prepares and runs sequential or prefetch stream closures to `io.Discard`.

## State and Persistence Behavior

State is in-memory chunk data and mock URL maps; no filer store is involved.

## Dependencies and Integration Points

Depends on production streaming APIs, `util_http.InitGlobalHttpClient`, `httptest`, `filer_pb.FileChunk`, and the `wdclient` lookup interface.

## Risks and Edge Cases

Benchmarks include preparation/lookup work inside timed loops, so results measure more than pure streaming. Random data generation is outside timed sections. Verification checks only size, not byte-by-byte equality.

## Test Signals

Useful performance signal for chunk counts, chunk sizes, latency, and prefetch width. Functional signal is limited to no-error and output length.
