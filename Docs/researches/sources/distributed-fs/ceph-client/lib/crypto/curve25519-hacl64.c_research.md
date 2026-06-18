# sources/distributed-fs/ceph-client/lib/crypto/curve25519-hacl64.c

## Purpose
64-bit HACL-derived generic Curve25519 backend using 5 51-bit limbs and 128-bit intermediates.

## Important APIs, Types, And Functions
Defines constant-time mask helpers, carry/reduction helpers, multiplication and squaring routines, `crecip`, point swap/copy functions, Montgomery ladder helpers, format expand/contract routines, and `curve25519_generic()`.

## Control Flow
The backend expands the basepoint into 51-bit limbs, clamps a local scalar copy, initializes projective ladder state, runs the ladder over all scalar bytes using conditional swaps and add/double steps, converts projective coordinates back by inverting `z`, contracts the field element to canonical 32-byte little-endian form, and wipes large temporary buffers and scalar copies.

## State, Persistence, And Dependencies
All state is stack-local, including aligned buffers for points and scalar. It depends on `u128`, unaligned little-endian accessors, and Curve25519 constants. No persistent global state exists.

## Integration Points
Used as `curve25519_generic` on 64-bit targets with 128-bit integer support when no arch override is selected by `curve25519.c`.

## Risks
Correctness depends on 128-bit arithmetic availability and carry bounds. Constant-time conditional swaps and trim masks must remain branchless. As with all X25519 code, low-order outputs are rejected by the wrapper, not by this backend itself.

## Test Signals
RFC7748 vectors, random scalar/basepoint comparisons against known-good implementations, low-order point wrapper tests, and compiler-output review for secret-dependent branches are important.
