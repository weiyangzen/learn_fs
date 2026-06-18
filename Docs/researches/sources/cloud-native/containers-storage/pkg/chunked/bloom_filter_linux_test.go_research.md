<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux_test.go

Purpose: tests and benchmarks for chunked cache bloom filters.

Important APIs/types/functions: cache initialization globals, `initCache`, `BenchmarkLookupBloomFilter`, `BenchmarkLookupBloomRaw`, `TestBloomFilter`, and `TestStressBloomHashFn`.

Control flow: `initCache` builds many digest tags and a bloom filter. `TestBloomFilter` first verifies generated digests are absent, then adds and checks each. `TestStressBloomHashFn` iterates hash counts and bit-array sizes, including empty input, to assert indexes are in bounds and masks have exactly one bit.

State/persistence: in-memory caches only.

Dependencies/integration: exercises `newBloomFilter`, `hashFn`, `makeBinaryDigest`, `appendTag`, and `writeCacheFileToWriter`.

Risks/test signal: protects against out-of-bounds bloom indexing and malformed single-bit masks. Benchmarks document the intended speedup path but do not assert performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux_test.go -->
