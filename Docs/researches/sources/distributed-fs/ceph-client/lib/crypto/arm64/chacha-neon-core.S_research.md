# sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha-neon-core.S

## Purpose
This ARM64 ASIMD assembly file implements ChaCha and HChaCha core functions, including a high-throughput multi-block XOR path.

## Important APIs, Types, And Functions
Exported symbols are `chacha_block_xor_neon`, `hchacha_block_neon`, and `chacha_4block_xor_neon`; `chacha_permute` is local. Read-only tables include `CTRINC` for counter increments, `ROT8` for byte rotations, and `.Lpermute` for tail permutation/overlap handling.

## Control Flow
`chacha_permute` runs the requested double rounds on one state. `chacha_block_xor_neon` permutes one block, adds original state words, xors 64 input bytes, and writes output. `hchacha_block_neon` emits the HChaCha words. `chacha_4block_xor_neon` constructs four or more counter states in parallel, runs vectorized rounds, adds original words, transposes lanes into byte streams, xors input, stores full blocks, and uses permutation/overlapping-store logic for 128-320 byte tails.

## State And Persistence
No global mutable state exists. The caller owns the ChaCha state and increments its counter in the C header after each call. Output buffers are written in place or out of place.

## Dependencies And Integration Points
It depends on Linux linkage/assembler macros and ASIMD. `arm64/chacha.h` calls it inside `scoped_ksimd()` when ASIMD is available and SIMD is usable.

## Risks And Edge Cases
Partial tail handling uses overlapping loads/stores and assumes caller-provided buffers satisfy the header's chunking expectations. Counter increment and overflow behavior are split between assembly and C wrapper. Round count must match caller expectations for ChaCha20 or reduced-round variants.

## Test Signals
ChaCha20 and HChaCha vectors, XChaCha tests, in-place encryption, lengths around 64/128/192/256/320 bytes, counter continuation tests, and ASIMD-disabled fallback comparisons are strong signals.
