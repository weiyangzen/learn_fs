# sources/distributed-fs/ceph-client/crypto/ecc_curve_defs.h

## Purpose
`ecc_curve_defs.h` provides static curve parameter definitions consumed by `ecc.c`. It defines NIST P-192, P-256, P-384, P-521, and Curve25519 constants in the internal `struct ecc_curve` format.

## Important APIs, Types, And Functions
- The file defines arrays for generator x/y coordinates, prime `p`, order `n`, coefficient `a`, and coefficient `b` for NIST curves.
- `static struct ecc_curve nist_p192`, `nist_p256`, `nist_p384`, and `nist_p521` are used by `ecc_get_curve()`.
- `static const struct ecc_curve ecc_25519` contains Curve25519 name, bit size, generator x coordinate, prime, and Montgomery coefficient.

## Control Flow
There is no executable control flow. Inclusion by `ecc.c` makes these static definitions available to curve lookup and arithmetic functions.

## State And Persistence
All data is static in-kernel constant-style curve metadata. The arrays are not declared `const` for every NIST object because the `ecc_curve` fields are non-const pointers, but callers treat them as immutable domain parameters.

## Dependencies And Integration Points
The file depends on `struct ecc_curve` from `<crypto/ecc_curve.h>` included by `ecc.c`. NIST definitions support ECDH and ECDSA. Curve25519 is exposed through `ecc_get_curve25519()` for users outside this subset.

## Risks And Edge Cases
Any constant error breaks all cryptographic operations on that curve. Limb ordering is little-endian 64-bit internal order, not byte-string order. P-521 uses 9 digits with only 521 significant bits, which drives special reduction and bounds behavior. Curve25519 lacks `n`, `b`, and `y` fields here because it is used differently than short-Weierstrass NIST curves.

## Test Signals
Known-answer ECDH/ECDSA tests indirectly verify NIST constants. Additional validation includes public-key equation checks for each generator, verifying `nG` is infinity, and cross-checking constants against FIPS/RFC sources.
