# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_bench_test.go

Purpose: benchmarks buffered versus streaming chunk-copy paths. It documents and measures the expected performance and allocation difference between `downloadChunkData` plus `uploadChunkData` and the `io.Pipe`-based `streamCopyChunkRange`.

Important APIs and helpers are `benchEnv`, `newBenchEnv`, `neturl`, `BenchmarkCopyChunk_Buffered`, `BenchmarkCopyChunk_Streamed`, and `humanByteName`. The fake source volume serves deterministic payload bytes and honors `Range`; the fake destination volume parses multipart upload bodies and verifies SHA-256 content integrity.

Control flow creates test servers per payload size, configures an `AssignVolumeResponse` pointing at the fake destination, initializes the global HTTP client, then runs benchmarks for 1 MiB, 8 MiB, and 64 MiB payloads. The buffered benchmark downloads the full chunk into memory and uploads it. The streamed benchmark calls `streamCopyChunkRange` with `isFullChunk=true` to exercise multipart pipe forwarding without a chunk-sized S3-side buffer.

State and persistence are local to benchmark servers and heap allocations. The destination server discards bytes after hashing; no filer state is used. The `AssignVolumeResponse` models the minimum volume assignment shape needed by upload code.

Dependencies include Go's benchmark framework, `httptest`, `multipart`, `sha256`, `filer_pb.AssignVolumeResponse`, and `util_http`. This file integrates with the copy implementation as a performance harness and compile-time sanity check that the standard multipart package remains available.

Risks and test signals: these are benchmarks, not pass/fail correctness tests except for benchmark fatal assertions. They are useful for detecting allocation regressions or throughput changes in streaming copy, but they do not exercise SSE, compression headers, destination auth failures, or real SeaweedFS volume servers.
