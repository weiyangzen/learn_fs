# sources/cloud-native/containerd/pkg/archive/compression/benchmark_test.go

## Purpose
Benchmarks decompression performance for gzip, zstd, and optional external gzip accelerators.

## Important APIs, Types, And Functions
`BenchmarkDecompression` downloads test data, expands it to 32/64/128/256 MiB, compresses it with helper functions, and benchmarks `testDecompress` with zstd, pure Go gzip, `igzip`, and `unpigz` when present.

## Control Flow
The benchmark mutates package global `gzipPath` to force decompressor selection and restores it after sub-benchmarks.

## State And Persistence
Downloads data from the network during benchmark execution and mutates `gzipPath` process-global state temporarily.

## Dependencies And Integration Points
Uses net/http, exec.LookPath, testing benchmarks, and package compression helpers.

## Risks
Network dependency makes benchmarks non-hermetic. Global `gzipPath` mutation means benchmarks should not run concurrently with other compression tests.

## Test Signals
Performance-only signal; not intended as correctness coverage.
