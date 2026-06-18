# sources/distributed-fs/ceph-client/lib/crypto/mldsa.c

## Purpose
Implements ML-DSA signature verification for the kernel crypto library, including FIPS 204 parameter sets, polynomial arithmetic, signature/public-key decoding, challenge reconstruction, and optional FIPS self-test.

## Important APIs, Types, and Functions
- Exports `mldsa_verify(enum mldsa_alg alg, const u8 *sig, size_t sig_len, const u8 *msg, size_t msg_len, const u8 *pk, size_t pk_len)`.
- Defines `struct mldsa_parameter_set`, `struct mldsa_ring_elem`, and `struct mldsa_verification_workspace`.
- Core arithmetic includes `Zq_mult()`, `ntt()`, and `invntt_and_mul_2_32()`.
- Decode/encode helpers include `decode_t1_elem()`, `decode_z()`, `decode_hint_vector()`, `sample_in_ball()`, `rej_ntt_poly()`, `use_hint()`, `use_hint_elem()`, and `encode_w1()`.
- KUnit may export `mldsa_use_hint()` when `CONFIG_CRYPTO_LIB_MLDSA_KUNIT_TEST` is enabled.

## Control Flow and State
Verification selects parameters by algorithm, validates public key and signature lengths, allocates a size-dependent workspace with `kmalloc()`, and frees it with `kfree_sensitive()` through cleanup attributes. It decodes `ctilde`, `z`, and hint vector `h`; rejects malformed z/h values; samples challenge `c`; computes `tr = H(pk)` and `mu = H(tr || domain || msg)`; then hashes reconstructed `w'_1` rows into `ctildeprime`. Each row generates matrix elements from `rho` on demand with SHAKE128, multiplies by decoded z in NTT form, subtracts challenge times scaled public key, inverse-transforms, applies hints, encodes `w1`, and feeds SHAKE256. Verification succeeds only when `ctildeprime` equals `ctilde`; the current compare is `memcmp()`.

## Dependencies and Integration Points
Depends on `<crypto/mldsa.h>`, SHAKE/SHA3 APIs, unaligned helpers, FIPS test vectors in `fips-mldsa.h`, allocation APIs, and module/export infrastructure. Integrated by crypto consumers needing public-key ML-DSA verification. Under `CONFIG_CRYPTO_FIPS`, module init verifies one ML-DSA-65 test vector and panics on failure.

## Risks and Test Signals
Arithmetic range bounds, Montgomery reduction assumptions, decoding malleability checks, hint ordering, and public-key/signature length validation are critical. `memcmp()` leaks first differing byte timing but compares public verification data; any change to secrecy assumptions should revisit this. Tests should include NIST/FIPS 204 vectors for ML-DSA-44/65/87, malformed signatures for z range and hint ordering/omega tails, public-key length/signature length errors, FIPS self-test, KUnit `use_hint()` edge cases around `Q - gamma2`, and cross-checks against a reference implementation.
