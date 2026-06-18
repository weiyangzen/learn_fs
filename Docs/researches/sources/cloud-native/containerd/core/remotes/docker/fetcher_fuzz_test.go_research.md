<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_fuzz_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/fetcher_fuzz_test.go

## Purpose
Fuzzes the Docker fetcher's low-level `open` path with arbitrary non-empty payloads served from a local HTTP server.

## Important APIs, Types, And Functions
- `FuzzFetcher(f *testing.F)` is the fuzz entry point.
- The test constructs a `dockerFetcher`, a `RegistryHost`, and a raw `GET` request, then calls `f.open`.

## Control Flow
Each fuzz input becomes server response data with matching `Content-Range` and `Content-Length`. The test opens offset zero, reads the whole body, and fails if the returned length differs from the original fuzz input.

## State And Persistence
All state is per-fuzz-iteration and in memory. Each iteration starts and closes its own `httptest.Server`.

## Dependencies And Integration Points
Exercises `dockerFetcher.open`, `dockerBase.request`, HTTP response header parsing, range validation, and body reading. It intentionally avoids content store integration and digest validation to focus on fetch transport behavior.

## Risks And Edge Cases
The fuzz currently checks length rather than byte-for-byte equality, so it catches truncation/expansion but not all content mutations. It skips empty data and silently returns on setup/open/read errors, which makes it a robustness fuzz rather than a strict oracle for every input.

## Test Signals
Provides broad randomized coverage of response sizes and byte patterns for the fetch open path, complementing deterministic range and encoding tests in `fetcher_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_fuzz_test.go -->
