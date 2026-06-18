# sources/cloud-native/buildkit/cache/contenthash/checksum_bench_test.go

Purpose: benchmarks vtproto serialization performance for persisted contenthash cache records.

Important APIs/types/functions: global `Buf` prevents marshal results from being optimized away; `CacheRecordsOutput` stores unmarshal output; `BenchmarkMarshalCacheRecords`, `BenchmarkUnmarshalCacheRecords`, and `sampleCacheRecords`.

Control flow: marshal benchmark repeatedly calls `MarshalVT` on sample records. Unmarshal benchmark first uses standard `proto.Marshal` to produce compatible bytes, then repeatedly calls `UnmarshalVT`. `sampleCacheRecords` builds a mix of directory, directory header, file, and symlink records with deterministic digests.

State and persistence behavior: no persistent writes; it models the same `CacheRecords` payload stored in ref metadata by `checksum.go`.

Dependencies and integration points: uses OpenContainers digest, testify require, protobuf runtime, and vtproto methods generated for `checksum.proto`.

Risks: benchmarks cover only a small fixed sample, not very large trees or pathological symlink/path mixes. They test speed and basic correctness through no-error assertions, not semantic equivalence after unmarshal.

Test signals: run with `go test -bench` in the contenthash package. Useful for detecting serialization regressions after proto or vtproto generator changes.
