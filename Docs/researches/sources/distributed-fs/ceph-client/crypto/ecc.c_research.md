# sources/distributed-fs/ceph-client/crypto/ecc.c

## Purpose
`ecc.c` is the shared elliptic-curve arithmetic implementation used by ECDH, ECDSA, and EC-RDSA. It provides curve lookup, big-integer limb helpers, modular arithmetic, point multiplication/addition, public/private key validation, public key generation, and ECDH shared secret computation.

## Important APIs, Types, And Functions
- `ecc_get_curve()` returns NIST P-192/P-256/P-384/P-521 curves, suppressing P-192 in FIPS mode. `ecc_get_curve25519()` returns the Curve25519 parameter struct.
- Conversion helpers include `ecc_digits_from_bytes()`, `vli_from_be64()`, `vli_from_le64()`, and exported compare/arithmetic helpers such as `vli_cmp()`, `vli_sub()`, `vli_mod_inv()`, and `vli_mod_mult_slow()`.
- `ecc_alloc_point()` and `ecc_free_point()` allocate and sensitive-free point coordinate buffers.
- Internal VLI routines implement addition, subtraction, multiplication, squaring, modular reduction, and inverse. Fast reducers cover NIST P-192/P-256/P-384/P-521, pseudo-Mersenne shapes, and Barrett fallback.
- Point routines include `ecc_point_double_jacobian()`, `xycz_add()`, `xycz_add_c()`, `ecc_point_mult()`, `ecc_point_add()`, and exported `ecc_point_mult_shamir()`.
- Key functions include `ecc_is_key_valid()`, `ecc_gen_privkey()`, `ecc_make_pub_key()`, `ecc_is_pubkey_valid_partial()`, `ecc_is_pubkey_valid_full()`, and `crypto_ecdh_shared_secret()`.

## Control Flow
Private key generation obtains random bytes from `crypto_stdrng_get_bytes()` and validates the result by rejection sampling bounds `[2, n-3]`. Public key generation multiplies the curve generator by the private key, then performs a full public-key validation check. Shared-secret computation parses the peer public key into a point, performs partial public-key validation, randomizes the initial projective Z coordinate with `get_random_bytes()`, multiplies by the private key, rejects the point at infinity, and returns the x coordinate.

ECDSA and ECRDSA verification use `ecc_point_mult_shamir()` to compute double-scalar multiplications. ECDH and public key generation use `ecc_point_mult()`, which is a Montgomery-ladder-style co-Z multiplication with scalar blinding by adding curve order variants before choosing a scalar representation.

## State And Persistence
The file has no mutable global runtime state, but includes static curve definitions through `ecc_curve_defs.h`. Allocated points and temporary arrays are per call. Sensitive point storage and random Z are cleared/freed where appropriate, though many stack temporaries are ordinary arithmetic buffers.

## Dependencies And Integration Points
This file depends on curve constants from `ecc_curve_defs.h`, kernel RNG APIs, FIPS mode, and crypto internal ECC headers. It exports symbols consumed by `ecdh.c`, `ecdsa.c`, `ecdsa-p1363.c`, `ecdsa-x962.c`, and `ecrdsa.c`.

## Risks And Edge Cases
This is high-risk arithmetic code. Correctness depends on limb order, curve-specific reduction, point-at-infinity handling, and scalar bounds. Public key validation has partial and full variants; ECDH uses partial validation for ephemeral keys, while ECDSA uses full validation on public keys. `ecc_get_curve()` can return NULL for P-192 in FIPS mode, so callers must handle unavailable curves. Timing side-channel behavior is mitigated in multiplication style but should not be assumed constant-time for every helper path.

## Test Signals
Testmgr contains ECDH vectors for P-192/P-256/P-384, ECDSA vectors for P-192/P-256/P-384/P-521, x962 and p1363 wrapper vectors, and ECRDSA vectors. Additional signals include invalid public points, point-at-infinity rejection, private key boundary rejection, FIPS P-192 unavailability, and cross-checking shared secrets/public keys against independent implementations.
