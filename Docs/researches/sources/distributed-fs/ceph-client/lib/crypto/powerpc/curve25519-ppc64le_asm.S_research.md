# sources/distributed-fs/ceph-client/lib/crypto/powerpc/curve25519-ppc64le_asm.S

## Purpose
Implements low-level 51-bit limb arithmetic primitives for PPC64 little-endian X25519 scalar multiplication. The C Montgomery ladder in `curve25519.h` calls these primitives for multiplication, squaring, repeated squaring, conversion, and conditional swaps.

## Important APIs, Types, and Functions
Exports `x25519_fe51_mul`, `x25519_fe51_sqr`, `x25519_fe51_mul121666`, `x25519_fe51_sqr_times`, `x25519_fe51_frombytes`, `x25519_fe51_tobytes`, and `x25519_cswap`. The functions operate on `fe51` arrays of five 64-bit limbs.

## Control Flow
Multiplication loads five limbs from both operands, computes cross-products with `mulld`/`mulhdu`, folds high limbs using the Curve25519 reduction factor 19, then branches into shared reduction logic. Squaring uses symmetry to reduce multiplications and also branches to shared reduction. `mul121666` multiplies all limbs by the Montgomery ladder constant and reduces. `sqr_times` runs the squaring/reduction body under a CTR loop. `frombytes` maps 32 little-endian bytes into five 51-bit limbs. `tobytes` performs full carry reduction, conditionally subtracts the field prime via carry propagation, and packs limbs back into 32 bytes. `x25519_cswap` performs a branchless masked swap over five limbs.

## State and Persistence
All field operations write results to caller-provided buffers. They preserve ABI-required nonvolatile registers using stack frames. No globals are modified.

## Dependencies and Integration Points
Included by the PowerPC Curve25519 arch implementation in `curve25519.h`. It depends on PPC64LE integer multiply/high-multiply support and Linux `SYM_FUNC_START` linkage macros.

## Risks
Finite-field arithmetic has high correctness sensitivity around carries, final reduction, and limb packing. Constant-time behavior depends on `x25519_cswap` remaining branchless with respect to secret bits and on avoiding secret-dependent memory indexing. There is an apparent duplicate restore of register 23 in `x25519_fe51_mul`, which is harmless but worth noticing during maintenance.

## Test Signals
Run RFC 7748 X25519 test vectors, random scalar multiplication comparisons against the generic implementation, and edge cases near field modulus boundaries. Constant-time review should focus on `x25519_cswap` and scalar-bit ladder integration.
