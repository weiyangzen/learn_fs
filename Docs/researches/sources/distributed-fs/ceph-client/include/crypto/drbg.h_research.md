# sources/distributed-fs/ceph-client/include/crypto/drbg.h

Purpose: internal/public structures and helpers for NIST SP800-90A DRBG implementations.

Important APIs/types/functions: `drbg_flag_t`, `struct drbg_core`, `struct drbg_state_ops`, `struct drbg_test_data`, `enum drbg_seed_state`, `struct drbg_state`, `drbg_statelen`, `drbg_blocklen`, `drbg_keylen`, max limit helpers, test wrappers for `crypto_rng_generate/reset`, DRBG type/strength flags, and prefix enum.

Control flow: DRBG operations are mediated by state ops for update/generate/crypto init/fini. RNG wrapper helpers pass additional input and test entropy into the crypto RNG API. Seed state tracks unseeded, partial, and full seeding.

State and persistence: `drbg_state` is substantial persistent RNG state: mutex, V/C/key material, reseed counters/thresholds, scratch buffers, CTR cipher/request/wait/SGs, seed status, last seed time, prediction resistance, FIPS continuous-test state, Jitter RNG handle, ops/core pointers, and test data.

Dependencies and integration points: depends on random, scatterlist, hash, skcipher, internal DRBG/RNG headers, FIPS, mutexes, lists, and workqueues. Integrates with kernel RNG crypto API.

Risks: RNG state is highly sensitive; locking, reseed thresholds, FIPS continuous tests, and partial-seed handling are security-critical. Test-only entropy injection must not leak into production paths.

Test signals: SP800-90A CAVP vectors for hash/HMAC/CTR modes, reseed limit tests, prediction-resistance tests, FIPS continuous-test failures, partial entropy boot tests, and lockdep around generate/reset.
