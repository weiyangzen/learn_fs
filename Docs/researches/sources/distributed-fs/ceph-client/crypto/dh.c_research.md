# sources/distributed-fs/ceph-client/crypto/dh.c

## Purpose
`dh.c` implements the generic Diffie-Hellman KPP algorithm and optional RFC7919 FFDHE safe-prime templates. The generic algorithm computes public keys and shared secrets with MPI modular exponentiation. The safe-prime templates bind well-known primes, generator 2, and private-key generation policy to the generic `dh` implementation.

## Important APIs, Types, And Functions
- `struct dh_ctx` stores MPI values `p`, `g`, and private exponent `xa`.
- `dh_set_secret()` decodes a serialized DH key, validates parameter length, imports `p`, `g`, and `xa`, and clears any old context.
- `dh_compute_value()` computes either `g^xa mod p` when `req->src` is NULL or `yb^xa mod p` when peer public key input is provided.
- `dh_is_pubkey_valid()` performs FIPS-mode SP800-56A public key validation for safe-prime groups.
- `struct dh_safe_prime` describes fixed FFDHE groups; the optional block under `CONFIG_CRYPTO_DH_RFC7919_GROUPS` defines FFDHE 2048 through 8192.
- `dh_safe_prime_gen_privkey()` generates a private key using SP800-56A rev3 oversampling and modular reduction for safe-prime groups.
- `dh_safe_prime_set_secret()` accepts optional key-only input, binds fixed `p`/`g`, auto-generates a key if absent, encodes the full secret, and delegates to spawned `dh`.
- `crypto_ffdhe_templates[]` registers `ffdhe2048`, `ffdhe3072`, `ffdhe4096`, `ffdhe6144`, and `ffdhe8192` templates when configured.

## Control Flow
The base `dh` KPP stores parameters during `set_secret`. Public-key generation and shared-secret computation share `dh_compute_value()`: allocate an MPI result, choose base from request input or `ctx->g`, validate peer base in FIPS mode, exponentiate, perform FIPS shared-secret/public-key checks, and write the MPI to the output scatterlist.

The safe-prime templates are normal KPP instances that spawn `dh`. Their `set_secret` path rejects caller-supplied `p` or `g`, fills in the fixed group, generates a private key if needed, encodes a normal DH secret blob, and calls `crypto_kpp_set_secret()` on the child transform. Generate/compute requests are forwarded through an embedded child request.

## State And Persistence
The base transform owns MPI allocations for `p`, `g`, and `xa`; `dh_clear_ctx()` frees and zeroes pointers. Safe-prime transform state owns a child KPP transform. Fixed group constants are static read-only data. Generated private keys and encoded buffers are freed with sensitive zeroing.

## Dependencies And Integration Points
The file depends on MPI arithmetic, `crypto_dh_decode_key()`/`crypto_dh_encode_key()` from `dh_helper.c`, kernel RNG via `crypto_stdrng_get_bytes()`, KPP spawn/instance helpers, and `fips_enabled`. It registers `dh` and optional `ffdhe*` crypto templates.

## Risks And Edge Cases
Generic DH only enforces minimum modulus length and `p != 0` through helper validation; outside FIPS mode, peer public-key validation is not performed. FIPS mode enforces `p >= 2048` and subgroup checks. Public key generation can return `-EAGAIN` if the generated key fails validation. Safe-prime private-key generation has subtle reduction logic and must preserve uniformity. Output write failures, negative MPI output signs, and `mod 0` hazards are explicitly handled.

## Test Signals
Useful tests include base DH known-answer KPP vectors, invalid serialized secrets, too-small modulus rejection, FIPS-mode public key validation failures, generated FFDHE private-key bounds, and child request forwarding. Testmgr in this tree emphasizes KPP vectors for ECDH; DH coverage may come from broader kernel crypto self-tests or consumers.
