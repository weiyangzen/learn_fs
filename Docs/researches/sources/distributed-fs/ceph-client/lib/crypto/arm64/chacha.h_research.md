# sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha.h

## Purpose
This header dispatches ARM64 ChaCha/HChaCha operations to ASIMD assembly when beneficial and safe, otherwise generic C.

## Important APIs, Types, And Functions
It declares `chacha_block_xor_neon`, `chacha_4block_xor_neon`, and `hchacha_block_neon`. It defines `have_neon`, `chacha_doneon`, `hchacha_block_arch`, `chacha_crypt_arch`, and `chacha_mod_init_arch`.

## Control Flow
`chacha_crypt_arch` falls back to generic code if ASIMD is unavailable, the message is at most one block, or SIMD is unusable. Otherwise it enters `scoped_ksimd()` and calls `chacha_doneon`, which processes up to five blocks per iteration, uses a stack buffer for a final single partial block, and advances `state->x[12]` by consumed blocks. HChaCha similarly chooses generic or NEON.

## State And Persistence
The ChaCha state is caller-owned but its block counter is updated by the wrapper. No key material is stored globally. The static key persists after init.

## Dependencies And Integration Points
It depends on `crypto/internal/simd.h`, jump labels, kernel helpers, ARM64 hwcap/SIMD, and common ChaCha state constants. It integrates with generic ChaCha/XChaCha library hooks.

## Risks And Edge Cases
Counter updates must match bytes processed, especially for partial final blocks. The wrapper copies short tails through a 64-byte stack buffer to satisfy assembly block assumptions. SIMD gating is mandatory in atomic/preempt-disabled contexts.

## Test Signals
ChaCha vectors over many lengths, counter wrap/continuation tests, HChaCha vectors, generic-vs-NEON comparison, and testing with `crypto_simd_usable()` false validate this header.
