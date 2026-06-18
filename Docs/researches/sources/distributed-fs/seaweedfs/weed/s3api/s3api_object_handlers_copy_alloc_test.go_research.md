# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_alloc_test.go

Purpose: regression-tests `downloadChunkData` allocation behavior for large server-side copy chunks. It specifically protects the fix for issue #6541, where appending streamed chunks to a nil slice caused geometric growth and roughly doubled memory allocation for each copied chunk.

Important API coverage is `TestDownloadChunkData_AllocationBound`, which initializes the global HTTP client, serves a 16 MiB payload through `httptest.Server`, warms up client/pool state, measures `runtime.MemStats.TotalAlloc` around a second download, and checks both byte-for-byte correctness and allocation budget.

Control flow builds deterministic payload bytes, writes them from the fake volume server in 64 KiB chunks with flushes, invokes `S3ApiServer.downloadChunkData`, compares the returned bytes after measurement, and fails if total allocation exceeds 1.5 times the payload size. The test intentionally measures after warmup and before `bytes.Equal` so validation work does not pollute allocation accounting.

State and persistence are in-memory only: a local HTTP server, global HTTP client initialization, GC-triggered runtime memory stats, and the returned byte slice. There is no filer or volume persistence.

Dependencies include `runtime`, `httptest`, `util_http.InitGlobalHttpClient`, and the implementation's global HTTP client. The integration signal is performance rather than API response behavior: it pins the implementation's pre-sized receive buffer contract.

Risks include allocator noise across Go versions or environments, but the bound is loose enough to distinguish the intended preallocated path from the old geometric append path. This test does not cover encrypted-chunk HEAD-size adjustment or retry behavior; it focuses narrowly on heap growth during normal streaming download.
