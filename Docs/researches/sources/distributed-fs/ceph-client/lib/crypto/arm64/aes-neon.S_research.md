# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-neon.S

## Purpose
This ARM64 file implements AES modes using pure ASIMD/NEON operations rather than ARMv8 AES instructions. It provides a fallback accelerated mode implementation when ASIMD exists but AES CE does not.

## Important APIs, Types, And Functions
By defining `AES_FUNC_START(func)` as `neon_ ## func` and including `aes-modes.S`, it emits `neon_aes_*` mode functions. Local macros implement AES S-box/substitution, MixColumns, ShiftRows, and 4-block encrypt/decrypt operations with vector table/permutation instructions. Read-only tables include forward/reverse ShiftRows and rotate-by-8 permutations.

## Control Flow
The file sets up NEON AES round transformations, xors round keys, applies ShiftRows and SubBytes, performs MixColumns or inverse MixColumns as needed, and delegates mode-specific loops to `aes-modes.S`. Multi-block paths process four blocks at a time using vectorized transformations.

## State And Persistence
No global mutable state is used. Mode state lives in caller buffers, IVs, counters, tweaks, and key schedules.

## Dependencies And Integration Points
It requires ASIMD and the shared mode template. `arm64/aes.h` selects this path for CBC-MAC and exported internal mode helpers when ASIMD is available but AES CE is not.

## Risks And Edge Cases
The software S-box/MixColumns implementation is more complex than CE instruction use and may have timing/microarchitectural concerns. It shares all tail and mode risks from `aes-modes.S`. Correct table constants are critical.

## Test Signals
AES mode selftests on ASIMD-only arm64 targets or with AES feature masked, generic/CE comparison, in-place and tail tests, and KASAN checks around partial-block temporary buffers validate this file.
