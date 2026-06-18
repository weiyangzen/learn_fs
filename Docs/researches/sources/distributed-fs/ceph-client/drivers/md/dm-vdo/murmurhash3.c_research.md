# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.c

## Purpose
`murmurhash3.c` provides a kernel-adapted implementation of MurmurHash3 x64 128-bit hashing for non-cryptographic hashing needs.

## Important APIs, Types, and Functions
The exported function is `murmurhash3_128(const void *key, const int len, const u32 seed, void *out)`. Helpers are `rotl64()`/`ROTL64` and `fmix64()` for final avalanche mixing.

## Control Flow
The function initializes two 64-bit hash lanes from the seed, processes 16-byte little-endian blocks with Murmur constants, handles a switch-based tail for 0-15 remaining bytes, xors in length, mixes the lanes together, finalizes each lane with `fmix64()`, mixes again, and stores two 64-bit words to `out`.

## State and Persistence Behavior
There is no state or persistence. Output is deterministic for key bytes, length, and seed.

## Dependencies and Integration Points
It uses Linux unaligned little-endian access helpers and compiler/types declarations from the header. It is suitable for in-kernel hash tables or content/index hashing where cryptographic security is not required.

## Risks and Edge Cases
The implementation writes `out` as `u64 *`, so callers must provide at least 16 bytes and tolerate unaligned stores if applicable. Length is `int`; negative lengths would be invalid caller behavior. It is not cryptographic and must not be used for adversarial integrity or authentication.

## Test Signals
Known MurmurHash3 x64_128 test vectors for multiple lengths, seeds, unaligned keys, and tail sizes 0-15 are the primary signals.
