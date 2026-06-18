# sources/distributed-fs/ceph-client/lib/crypto/curve25519-fiat32.c

## Purpose
32-bit Fiat-derived generic Curve25519 scalar multiplication backend using 10-limb field arithmetic.

## Important APIs, Types, And Functions
Defines `fe` and `fe_loose` limb types, field helpers such as `fe_frombytes`, `fe_tobytes`, `fe_add`, `fe_sub`, `fe_mul_*`, `fe_sq_*`, `fe_invert`, `fe_cswap`, `fe_mul121666`, and exports implementation symbol `curve25519_generic()`.

## Control Flow
Inputs are decoded into field elements, the scalar is copied and clamped, and a Montgomery ladder iterates from bit 254 down to 0. Each step conditionally swaps projective points in constant-time, performs differential addition and doubling with loose/tight field elements, and updates the swap flag. After the loop it swaps once more, inverts `z`, multiplies to recover affine `x`, serializes 32 bytes, and zeroes the scalar.

## State, Persistence, And Dependencies
All arithmetic state is stack-local. The caller receives only the public output. It depends on Curve25519 header helpers, fixed-width integer types, and generated Fiat arithmetic invariants.

## Integration Points
Selected by `curve25519.c` when no arch backend exists and the build target does not use the HACL64 backend. It provides the same `curve25519_generic` ABI as the 64-bit backend.

## Risks
Constant-time behavior depends on `fe_cswap` and generated arithmetic not being optimized into branches. Limb bounds must match Fiat preconditions. Stack-local secret scalar is wiped, but intermediate field elements also contain secret-dependent values and rely on stack lifetime.

## Test Signals
RFC7748 vectors, all-zero and low-order point rejection via wrapper, randomized cross-checks against HACL64 or arch backends, and side-channel review of generated code are key signals.
