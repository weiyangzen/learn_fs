# sources/distributed-fs/ceph-client/crypto/ecdh.c

## Purpose
`ecdh.c` registers generic ECDH KPP algorithms for NIST P-192, P-256, and P-384. It adapts serialized ECDH secrets and scatterlist KPP requests to the shared ECC arithmetic layer.

## Important APIs, Types, And Functions
- `struct ecdh_ctx` stores selected curve id, digit count, and private key limbs.
- `ecdh_set_secret()` decodes a serialized ECDH key. Empty key material triggers private-key generation; supplied key material is converted and range-validated.
- `ecdh_compute_value()` generates a public key when `req->src` is NULL or computes a shared secret when peer public key input is supplied.
- `ecdh_max_size()` reports two-coordinate public key size.
- `ecdh_nist_p192_init_tfm()`, `ecdh_nist_p256_init_tfm()`, and `ecdh_nist_p384_init_tfm()` bind curve parameters to registered KPP algorithms.

## Control Flow
`set_secret` clears the private key array, decodes the buffer via `crypto_ecdh_decode_key()`, and either calls `ecc_gen_privkey()` or imports caller bytes with `ecc_digits_from_bytes()` followed by `ecc_is_key_valid()`. Compute allocates a public key buffer and, for shared secrets, a secret buffer. Peer public keys must be exactly two coordinates. Data is copied from request scatterlist, passed to `crypto_ecdh_shared_secret()` or `ecc_make_pub_key()`, then copied back to the destination scatterlist.

## State And Persistence
The transform context persists the private key in a fixed `u64[ECC_MAX_DIGITS]` array. Temporary public/secret buffers are heap allocated per request and secret output buffers are freed with `kfree_sensitive()`.

## Dependencies And Integration Points
The file depends on `ecdh_helper.c` for key decode, `ecc.c` for key generation/public/shared-secret operations, KPP crypto registration, and scatterlist helpers. It registers `ecdh-nist-p192`, `ecdh-nist-p256`, and `ecdh-nist-p384`; P-192 registration may fail in FIPS mode.

## Risks And Edge Cases
The code must handle FIPS-mode P-192 unavailability and curve lookup failures from the ECC layer. Destination output is truncated to `req->dst_len`, so callers can request less than full public key/secret. Invalid peer public key length or scatterlist copy failure returns `-EINVAL`. Private key clearing on invalid supplied key uses `params.key_size`, which is byte length, against a limb array; current keys fit the array but changes should preserve safe clearing.

## Test Signals
`testmgr.h` includes `ecdh_p192_tv_template`, `ecdh_p256_tv_template`, and `ecdh_p384_tv_template`; `testmgr.c` maps the three registered algorithms. Useful tests include generated key path, explicit private key path, invalid peer length, truncated destination length, and FIPS P-192 registration behavior.
