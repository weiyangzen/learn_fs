<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux.go -->
# sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux.go

Purpose: simple serialized bloom filter used by chunked layer cache files to avoid binary-searching digest tags for definitely-absent digests.

Important APIs/types/functions: `bloomFilterMaxLength`, `bloomFilter`, `newBloomFilter`, `newBloomFilterFromArray`, `hashFn`, `add`, `maybeContains`, `writeTo`, and `readBloomFilter`.

Control flow: `newBloomFilter` rounds bit array length to uint64 slots and guarantees at least one slot. `hashFn` uses CRC32 over seed-split slices modulo bit count to produce an array index and single-bit mask. `add` sets `k` bits; `maybeContains` checks all `k`. Serialization writes array length, `k`, and raw uint64 array in little endian; deserialization caps length at 100 MB before allocation.

State/persistence: serialized inside chunked cache big-data blobs. In memory, it is part of `cacheFile`.

Dependencies/integration: used by `cache_linux.go` when writing and reading layer lookaside caches and in `findDigestInternal`.

Risks: CRC32 hash functions are not cryptographic and false positives are expected; correctness relies on a later exact tag lookup. The max length check is important for malformed cache DoS resistance.

Test signals: `bloom_filter_linux_test.go` checks add/maybeContains behavior, hash bounds/masks over many sizes, and benchmarks bloom-assisted lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux.go -->
