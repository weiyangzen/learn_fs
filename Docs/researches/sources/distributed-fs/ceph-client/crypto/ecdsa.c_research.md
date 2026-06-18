# sources/distributed-fs/ceph-client/crypto/ecdsa.c

## Purpose
`ecdsa.c` implements generic ECDSA signature verification for NIST P-192, P-256, P-384, and P-521 and registers the raw ECDSA signature algorithms plus x962 and p1363 encoding templates.

## Important APIs, Types, And Functions
- `struct ecc_ctx` stores curve id, curve pointer, public-key-set flag, coordinate buffers, and `struct ecc_point pub_key`.
- `_ecdsa_verify()` performs the ECDSA verification equation over already-parsed hash, r, and s limbs.
- `ecdsa_verify()` adapts the crypto sig API: checks public key presence, raw signature size, truncates digest to curve digit length, imports the digest, and calls `_ecdsa_verify()`.
- `ecdsa_set_pub_key()` parses RFC5480 uncompressed public keys (`0x04 || X || Y`) and fully validates the point.
- `ecdsa_key_size()` and `ecdsa_digest_size()` report curve bits and maximum supported digest size (`SHA512_DIGEST_SIZE`).
- Four `sig_alg` objects register `ecdsa-nist-p192`, P-256, P-384, and P-521.
- `ecdsa_init()` also registers `ecdsa_x962_tmpl` and `ecdsa_p1363_tmpl`.

## Control Flow
Setting a public key resets the context, validates uncompressed encoding and coordinate size, imports X and Y, then calls `ecc_is_pubkey_valid_full()`. Verification rejects missing public keys or wrong raw signature size, imports at most one curve-width of digest bytes, verifies `0 < r,s < n`, computes `s^-1`, derives `u1 = hash*s^-1 mod n` and `u2 = r*s^-1 mod n`, computes `u1G + u2Q` with Shamir's trick, reduces x modulo n, and compares it to r.

## State And Persistence
Per-transform state stores the selected curve and public key. There is no private key or signing state. Module-level state tracks whether P-192 registration succeeded because FIPS mode may suppress that curve.

## Dependencies And Integration Points
The file depends on `ecc.c` for arithmetic, `crypto/internal/sig.h` for signature registration, SHA-2 digest size constants, and external template objects declared in internal sig headers. It is the child algorithm used by `ecdsa-x962.c` and `ecdsa-p1363.c`.

## Risks And Edge Cases
This code verifies only; it does not sign. Digest truncation to curve length follows ECDSA practice but must be consistent with test vectors. P-192 can be unavailable in FIPS mode. Public key validation is full, including `nQ == infinity`, which is stronger but more expensive. Raw signature input must already be in internal limb struct format; external encodings need wrappers.

## Test Signals
`testmgr.h` includes raw ECDSA vectors for all four NIST curves and wrapper vectors for x962/p1363. Tests should cover invalid r/s zero or >= n, wrong public key format, invalid curve point, digest longer than curve size, and FIPS P-192 behavior.
