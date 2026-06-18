# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce-core.S

## Purpose
This ARM64 assembly file implements single-block AES primitives using ARMv8 Crypto Extensions. It is the core used by high-level AES encryption/decryption and key schedule helpers.

## Important APIs, Types, And Functions
Exported symbols are `__aes_ce_encrypt`, `__aes_ce_decrypt`, `__aes_ce_sub`, and `__aes_ce_invert`. The first two process one 16-byte block with a provided round-key schedule and round count. `__aes_ce_sub` uses `aese` as an S-box primitive for key expansion, and `__aes_ce_invert` applies `aesimc` for decryption key derivation.

## Control Flow
Encrypt/decrypt load the input block and round keys, execute AES rounds in a compact loop that adapts to AES-128/192/256 round counts, apply final `aese`/`aesd` without MixColumns, xor the last round key, and store output. The helper routines are straight-line single-instruction transformations around loads/stores.

## State And Persistence
No persistent state exists. The caller-provided output buffer and key schedule are the only memory effects.

## Dependencies And Integration Points
It requires `.arch armv8-a+crypto`, Linux linkage, and is called by `arm64/aes.h` inside `scoped_ksimd()` when AES instructions are available.

## Risks And Edge Cases
Wrong round count or key schedule layout corrupts results. Dispatch must prevent execution on CPUs without AES instructions. The implementation assumes 16-byte block buffers and a compatible expanded-key format.

## Test Signals
AES ECB known-answer tests for 128/192/256-bit keys, key expansion tests exercising `__aes_ce_sub` and `__aes_ce_invert`, fallback comparison with scalar AES, and CPU feature gating tests validate this file.
