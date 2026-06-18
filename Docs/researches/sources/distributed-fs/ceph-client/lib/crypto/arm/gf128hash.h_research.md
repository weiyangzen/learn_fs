# sources/distributed-fs/ceph-client/lib/crypto/arm/gf128hash.h

## Purpose
This ARM32 header provides GHASH acceleration glue using NEON `vmull.p8` polynomial multiplication. It supplies an architecture-specific `ghash_blocks_arch` hook for the common GF(2^128) hashing layer.

## Important APIs, Types, And Functions
It declares `pmull_ghash_update_p8(size_t blocks, struct polyval_elem *dg, const u8 *src, const struct polyval_elem *h)`, defines `have_neon`, implements `ghash_blocks_arch`, and defines `gf128hash_mod_init_arch`.

## Control Flow
Initialization enables `have_neon` when `HWCAP_NEON` is present. `ghash_blocks_arch` checks the static key and `may_use_simd()`. On the fast path it processes input in chunks capped at 4096 bytes, entering `scoped_ksimd()` for each chunk so long GHASH operations allow rescheduling. Otherwise it calls `ghash_blocks_generic`.

## State And Persistence
Persistent state is only the feature static key. The accumulator `acc`, hash key `key->h`, and input stream are caller-owned and updated in memory by the chosen implementation.

## Dependencies And Integration Points
The header depends on ARM hwcap, NEON, SIMD helpers, `struct ghash_key`, `struct polyval_elem`, `GHASH_BLOCK_SIZE`, and generic GHASH fallback helpers. It is included by the common GF128 hash implementation when building ARM32 crypto.

## Risks And Edge Cases
The fast path assumes `nblocks > 0`; callers should avoid empty work or tolerate a no-op loop contract. SIMD use must remain guarded. The 4 KiB chunking is important for scheduler latency and should be preserved if the function is refactored.

## Test Signals
Signals include GHASH known-answer tests, AES-GCM crypto selftests, fallback-vs-NEON comparisons, preemptible kernel runs with large messages, and ARM32 builds with and without `CONFIG_KERNEL_MODE_NEON`.
