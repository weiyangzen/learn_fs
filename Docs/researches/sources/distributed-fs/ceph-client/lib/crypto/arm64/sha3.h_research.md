# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3.h

## Purpose
ARM64 SHA3 dispatch header that replaces generic absorb and Keccak permutation with SHA3 CE implementations when available.

## Important APIs, Types, And Functions
Declares `sha3_ce_transform`, defines static key `have_sha3`, overrides `sha3_absorb_blocks()` and `sha3_keccakf()`, and provides `sha3_mod_init_arch()`.

## Control Flow
Absorb uses CE when the static key is enabled and `may_use_simd()` succeeds; otherwise it calls `sha3_absorb_blocks_generic()`. `sha3_keccakf()` uses the CE transform with a static zero block and `SHA3_512_BLOCK_SIZE` to run a plain permutation, or falls back to `sha3_keccakf_generic()`.

## State, Persistence, And Dependencies
State is caller-owned `sha3_state`. Persistent state is the static key enabled on `cpu_have_named_feature(SHA3)`. Dependencies include kernel SIMD helpers and CPU feature detection.

## Integration Points
Used by the generic SHA3/SHAKE implementation and by FIPS SHA3-256 self-test vectors.

## Risks
The zero-block permutation trick depends on transform semantics: zero input must only trigger Keccak-f without changing absorbed lanes. SIMD gating must protect vector registers. Unsupported rates must not reach the assembly path.

## Test Signals
SHA3 and SHAKE vectors across all rates, tests invoking finalization with no pending data, and fallback-vs-CE comparisons validate this header.
