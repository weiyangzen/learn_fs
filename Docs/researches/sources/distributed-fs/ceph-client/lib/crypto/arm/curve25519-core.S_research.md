# sources/distributed-fs/ceph-client/lib/crypto/arm/curve25519-core.S

## Purpose
This ARMv7 NEON assembly file implements `curve25519_neon`, a kernel-space X25519 scalar multiplication routine. It derives from SUPERCOP/Bernstein-Schwabe code but is rewritten for Linux calling conventions and kernel SIMD use. It computes `out = scalar * point` over Curve25519 using radix-limb field arithmetic, a Montgomery ladder, and final inversion.

## Important APIs, Types, And Functions
The sole exported entry is `ENTRY(curve25519_neon)`, matching the header prototype `curve25519_neon(u8 out[32], const u8 secret[32], const u8 basepoint[32])`. Internal state is stack-resident field elements, stored as 10 alternating 25/26-bit limbs. Important labels are `.Lmainloop` for the 255-bit ladder, `.Linvertloop` and `.Lsquaringloop` for exponentiation-based inversion, and final carry/serialization code that writes the 32-byte little-endian result.

## Control Flow
The function saves callee registers, allocates an aligned 704-byte frame, clamps the scalar, decodes the input point into limbs, initializes projective ladder points, then iterates bits from 254 down to 0. Each ladder step conditionally swaps point coordinates with bit-mask NEON operations, performs differential addition and doubling with vectorized multiply/add/reduce sequences, and stores limbs back to stack slots. After the ladder, it computes `z^-1` through a fixed sequence of squarings and multiplications, multiplies by `x`, normalizes carries, and packs limbs to bytes.

## State And Persistence
All state is transient: stack slots hold scalar bytes, constants, intermediate field elements, and ladder state. The routine updates only the caller-provided output buffer and has no persistent storage. Secret-dependent control flow is avoided in the ladder by mask-based swaps; loop counts are fixed by scalar length and inversion schedule.

## Dependencies And Integration Points
It depends on `<linux/linkage.h>`, ARMv7-A, and NEON. `curve25519.h` calls it only inside `scoped_ksimd()` when the NEON static key is enabled and SIMD is usable. The generic Curve25519 implementation is the fallback.

## Risks And Edge Cases
Correctness depends on exact limb bounds, carry propagation, scalar clamping, and final canonicalization modulo `2^255-19`. The large hand-written frame makes offset drift risky. Kernel callers must not enter this function without SIMD context protection. Side-channel risk centers on unintended secret-dependent memory/control behavior and microarchitectural leakage in vector arithmetic.

## Test Signals
Use X25519 known-answer tests, Wycheproof-style public key edge cases including all-zero and high-bit encodings, differential tests against `curve25519_generic`, KASAN/KMSAN stack checks, ARM32 NEON boot tests, and crypto selftests under preemption/softirq contexts that exercise `crypto_simd_usable()` gating.
