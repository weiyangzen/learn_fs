# sources/distributed-fs/ceph-client/lib/xxhash.c

## Purpose
Provides kernel xxHash 32-bit and 64-bit non-cryptographic hashing, with one-shot `xxh32`/`xxh64` and streaming 64-bit hashing.

## APIs and control flow
Exports `xxh32`, `xxh64`, `xxh64_reset`, `xxh64_update`, and `xxh64_digest`. One-shot functions process 16- or 32-byte stripes with unaligned little-endian loads, handle remaining tail bytes, then avalanche the result. Streaming state initializes four accumulators from the seed, buffers partial data until a 32-byte stripe is available, updates accumulators incrementally, and digests buffered tail data.

## State, dependencies, and integration
One-shot calls are stateless. Streaming state is caller-owned in `struct xxh64_state`; callers must reset before update/digest and serialize concurrent mutation. Dependencies are unaligned accessors, errno, kernel/string helpers, module exports, and `linux/xxhash.h`. The code integrates with compression, filesystem, deduplication, and hash-table style users that need fast deterministic hashes.

## Risks and test signals
xxHash is not cryptographic and must not protect secrets or authenticate data. Callers must pass valid memory for the declared length. Tests should use upstream xxHash vectors for seeds, short/long inputs, streaming split boundaries, unaligned buffers, and cross-endian stable output.
