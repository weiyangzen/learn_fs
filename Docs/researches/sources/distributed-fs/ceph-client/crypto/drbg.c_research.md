# sources/distributed-fs/ceph-client/crypto/drbg.c

## Purpose
`drbg.c` implements NIST SP800-90A deterministic random bit generators as kernel crypto RNG algorithms. Depending on configuration, it registers CTR-DRBG with AES, Hash-DRBG with SHA-2, and HMAC-DRBG with SHA-2, each with prediction-resistance and no-prediction-resistance variants under the `stdrng` algorithm name.

## Important APIs, Types, And Functions
- `drbg_cores[]` defines supported cores, security strength flags, state length, block length, public driver suffix, and backend crypto name.
- `struct drbg_state` is allocated as the RNG transform context and holds `V`, `C`, scratch buffers, backend handles, reseed counters, seed state, FIPS continuous-test state, and optional Jitter RNG handle.
- `drbg_ctr_update()` / `drbg_ctr_generate()`, `drbg_hash_update()` / `drbg_hash_generate()`, and `drbg_hmac_update()` / `drbg_hmac_generate()` implement the DRBG type-specific SP800-90A algorithms.
- `drbg_seed()`, `__drbg_seed()`, `drbg_seed_from_random()`, and `drbg_get_random_bytes()` collect entropy, mix personalization/additional input, update state, and set reseed thresholds.
- `drbg_generate()` performs API validation, reseed checks, prediction-resistance behavior, additional-input handling, generation, and reseed counter increment.
- `drbg_generate_long()` slices large requests into max-request-sized chunks.
- `drbg_alloc_state()` / `drbg_dealloc_state()` allocate aligned V/C/scratch/FIPS buffers and backend crypto handles.
- `drbg_kcapi_seed()`, `drbg_kcapi_random()`, and `drbg_kcapi_set_entropy()` adapt the implementation to `struct rng_alg`.
- `drbg_fill_array()` creates two registered RNG algorithms for each core: `drbg_pr_*` and `drbg_nopr_*`.

## Control Flow
Module initialization first runs FIPS sanity checks when required, fills the `drbg_algs` array, and registers all configured RNG variants. A transform initializes only its mutex at `cra_init`; real DRBG state is allocated during `seed`, where `drbg_convert_tfm_core()` maps the driver name to a core and PR flag. Instantiation allocates backend state, optionally prepares `jitterentropy_rng`, then seeds from test data or kernel RNG/Jitter RNG.

Generation locks the DRBG state per chunk. It validates buffer and additional-input sizes, marks the state unseeded if the reseed threshold is exceeded, reseeds for PR or unseeded state, opportunistically reseeds when the kernel RNG becomes fully initialized or the no-PR interval elapses, then calls the selected type-specific generate function. CTR uses `crypto_drbg_ctr_df()` plus a spawned `ctr(aes)` skcipher; Hash uses a hash derivation function and hashgen; HMAC updates key `C` and value `V` through HMAC.

## State And Persistence
Transform state persists for the crypto RNG handle lifetime. Critical state includes `V`, `C`, reseed counter, seed state (`UNSEEDED`, `PARTIAL`, `FULL`), last seed time, reseed threshold, backend handles, scratch buffers, and FIPS previous entropy sample. `drbg_uninstantiate()` frees backend handles and sensitive buffers but preserves test data. No state survives module unload or transform destruction.

## Dependencies And Integration Points
The file integrates with the crypto RNG API, shash API for Hash/HMAC DRBG, skcipher API for CTR DRBG, `df_sp80090a.c` for CTR derivation, `get_random_bytes()` and `rng_is_initialized()`, optional Jitter RNG, `fips_enabled`, and crypto testmgr. It exports aliases such as `drbg_nopr_hmac_sha512`, `drbg_pr_ctr_aes128`, and `stdrng`.

## Risks And Edge Cases
DRBG correctness depends on exact SP800-90A state transitions, scratch buffer sizing, and backend return-code handling. FIPS continuous RNG testing can panic on repeated entropy samples. In FIPS mode, Jitter RNG failure is fatal for initial seed and most non-transient failures, but transient reseed failures are tolerated according to comments. Test mode is indicated by an empty `test_data.list`, an unusual convention that affects entropy and reseeding behavior. Large requests are chunked, so additional input can be applied to multiple chunks if supplied to `drbg_generate_long()`.

## Test Signals
`testmgr.h` contains known-answer vectors for `drbg_pr_sha256`, `drbg_pr_hmac_sha256`, `drbg_pr_ctr_aes128`, no-PR SHA/HMAC/CTR variants, and HMAC-SHA512. `testmgr.c` maps many higher-strength variants as covered by representative vectors. Additional signals include max-additional-input rejection, max-request rejection, personalization handling through `seed`, partial-to-full reseed transition after `rng_is_initialized()`, and FIPS sanity/error-path checks.
