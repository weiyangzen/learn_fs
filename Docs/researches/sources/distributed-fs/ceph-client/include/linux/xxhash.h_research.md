# sources/distributed-fs/ceph-client/include/linux/xxhash.h

## Purpose
Declares the in-kernel xxHash interface for fast non-cryptographic hashing. The header exposes one-shot 32-bit and 64-bit hashes, a word-size convenience wrapper, and streaming xxh64 state operations.

## Important APIs, Types, and Functions
`xxh32()` hashes a byte range with a 32-bit seed and returns a 32-bit hash. `xxh64()` hashes a byte range with a 64-bit seed and returns a 64-bit hash. `xxhash()` is an inline word-size selector that calls `xxh64()` on 64-bit builds and `xxh32()` on 32-bit builds when cross-machine stability is not required. `struct xxh64_state` stores private streaming state: total length, four accumulators, a partial 32-byte buffer, and buffered byte count. Streaming calls are `xxh64_reset()`, `xxh64_update()`, and `xxh64_digest()`.

## Control Flow
One-shot callers pass the complete input, length, and seed directly to `xxh32()` or `xxh64()`. Streaming callers reset a state with a seed, call `xxh64_update()` for each chunk, and call `xxh64_digest()` whenever a current hash is needed; digesting does not finalize or prevent later updates.

## State and Persistence
The one-shot APIs own no persistent state. Streaming state persists in caller-allocated `struct xxh64_state` and must not be inspected or modified directly despite the visible fields. The seed and accumulated byte sequence determine reproducible results for a fixed algorithm width.

## Dependencies and Integration Points
Depends only on Linux integer and size types. Integrates with kernel code that needs fast checksums or hash-table keys where collision resistance is not a security boundary, such as compression metadata, deduplication hints, caches, or content fingerprints.

## Risks
xxHash is not cryptographic and must not protect against adversarial collision or integrity attacks. `xxhash()` intentionally varies with word size, so persistent on-disk or network formats should choose `xxh32()` or `xxh64()` explicitly. Streaming state layout is visible for allocation only and should not become an ABI.

## Test Signals
Signals include known-vector tests for `xxh32`/`xxh64`, chunked-versus-one-shot equivalence, 32-bit and 64-bit build coverage for `xxhash()`, unaligned input tests, and fuzzing around zero-length and partial-buffer updates.
