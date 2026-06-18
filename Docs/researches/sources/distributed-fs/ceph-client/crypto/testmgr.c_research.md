# sources/distributed-fs/ceph-client/crypto/testmgr.c

## Purpose
`testmgr.c` is the Linux crypto algorithm self-test manager for this source tree. It exports `alg_test()`, which is invoked when crypto algorithms are being tested after registration or explicit test requests, and dispatches to known-answer, API-behavior, FIPS-gating, and optional randomized comparison tests for symmetric ciphers, AEADs, hashes/MACs, compression, DRBGs, key-agreement, public-key encryption, and signature algorithms.

When `CONFIG_CRYPTO_SELFTESTS` is disabled, `alg_test()` is compiled as a no-op. When enabled, the file includes `testmgr.h`, defines a large sorted `alg_test_descs[]` table of roughly 230 algorithm descriptors, and binds each algorithm name to the appropriate test function, generic reference implementation name, FIPS allowance flag, and static test-vector suite.

## Important APIs, Types, And Functions
- Exported API: `int alg_test(const char *driver, const char *alg, u32 type, u32 mask)` is exported with `EXPORT_SYMBOL_GPL()` and declared in `crypto/internal.h`. It is the file's integration boundary with the crypto core.
- Module parameters: `notests` disables self-tests outside FIPS mode. Under `CONFIG_CRYPTO_SELFTESTS_FULL`, `noslowtests` disables slow fuzz/comparison tests and `fuzz_iterations` controls randomized test volume.
- Test suite descriptors: `struct alg_test_desc` maps `.alg` names to a `.test` callback, optional `.generic_driver`, `.fips_allowed`, and one union member among `aead`, `cipher`, `comp`, `hash`, `drbg`, `akcipher`, `sig`, and `kpp`.
- Layout model: `struct testvec_config` and `struct test_sg_division` describe scatterlist splits, offsets, relative alignmask offsets, in-place mode, request flags, hash finalization mode, and SIMD-disabling toggles.
- Buffer helpers: `__testmgr_alloc_buf()`, `testmgr_alloc_buf()`, `init_test_sglist()`, `build_test_sglist()`, `build_cipher_test_sglists()`, `verify_correct_output()`, and `is_test_sglist_corrupted()` allocate page-backed buffers, construct scatterlists, poison unused bytes, and detect output overruns or request/scatterlist corruption.
- Randomized helpers: `init_rnd_state()`, `generate_random_length()`, `generate_random_bytes()`, `generate_random_testvec_config()`, and algorithm-specific random vector generators produce adversarial but reproducible-at-runtime shapes for full self-tests.
- Generic-driver support: `build_generic_driver_name()` derives names such as `cbc(aes-generic)` or nested template forms, while descriptor entries override it where kernel naming conventions differ.
- Per-family test drivers: `alg_test_hash()`, `alg_test_aead()`, `alg_test_skcipher()`, `alg_test_cipher()`, `alg_test_comp()`, `alg_test_drbg()`, `alg_test_kpp()`, `alg_test_akcipher()`, `alg_test_sig()`, and `alg_test_null()` allocate the transform type and run the relevant vector harness.

## Control Flow
`alg_test()` first honors `notests` only when FIPS is not enabled, then runs `testmgr_onetime_init()` once via `DO_ONCE()`. That initializer checks the descriptor table sort/duplicate invariant and validates the built-in default cipher/hash test-vector configurations.

For single-block `CRYPTO_ALG_TYPE_CIPHER`, `alg_test()` wraps the algorithm name as `ecb(<alg>)`, looks it up with binary search in `alg_find_test()`, applies FIPS gating, and runs `alg_test_cipher()`. For other algorithm types, it looks up both the canonical algorithm name and the driver name, runs each matching descriptor's callback, and ORs the return codes. If no descriptor exists, `LSKCIPHER` gets a fallback `ecb(<alg>)` lookup and otherwise the function logs "No test"; FIPS-internal algorithms without accepted descriptors are rejected through `alg_fips_disabled()`.

Hash testing allocates an ahash transform and request, optionally also a shash transform and descriptor, then runs every static vector through both APIs where possible. Each vector is tested across default hash configurations and, in full mode, random configurations. Slow hash testing can generate vectors from a generic implementation and replay them against the target driver while checking digest size and block size consistency.

AEAD and skcipher testing share scatterlist infrastructure. For each vector, they test encryption and decryption across in-place-one-sglist, in-place-two-sglist, out-of-place, misaligned, split, MAY_SLEEP, page-crossing, and randomized layouts. After each operation, the harness checks request fields, source/destination scatterlist integrity, expected error codes, output bytes, overrun poison, and for skcipher optional output IV. Slow AEAD tests add generic implementation comparison and deliberately inauthentic ciphertext/AAD generation to verify decryption failure paths.

Compression tests allocate acomp requests for static compression and decompression vectors, verify round-trip output length/content, and directly compare decompression vectors. DRBG tests replay CAVS-style entropy, personalization, additional input, prediction-resistance entropy, and expected output through the rng/drbg test hooks. KPP tests generate public keys and compute shared secrets for both fixed and generated-key vectors. Akcipher tests verify encryption and, when private keys are available, decryption. Signature tests verify cooked signatures first and, for private-key vectors, generate signatures and compare exact output.

## State And Persistence Behavior
The file keeps no persistent on-disk state. State is local to kernel memory allocated during a specific `alg_test()` call, request contexts, scatterlist buffers, randomized test vectors, and per-CPU SIMD-disable state while full self-tests intentionally execute operations in no-SIMD sections.

The durable effects are crypto-core side effects outside this file: callers use the return value to mark algorithms as tested or failed, and FIPS failure paths call `fips_fail_notify()` and panic on self-test failure. Runtime knobs are module parameters, so they are externally visible via module/sysfs parameter handling but do not persist test results here.

## Dependencies And Integration Points
This file depends heavily on the kernel crypto API headers for AEAD, hash, skcipher, rng/DRBG, akcipher, KPP, acomp, sig, internal cipher, and internal SIMD control. It uses kernel support for scatterlists, page allocation, slab allocation, iov iteration, random-prandom generation, FIPS status, module parameters, waits, and once-only initialization.

`testmgr.h` supplies the static test-vector templates referenced by `alg_test_descs[]`. `algboss.c` calls `alg_test()` during algorithm test work and then calls `crypto_alg_tested()`. `tcrypt.c` can call `alg_test()` directly for manual test module modes. `drbg.c` invokes specific DRBG self-tests. `algapi.c`, `api.c`, and `/proc/crypto` handling consume the tested/untested outcome via `CRYPTO_ALG_TESTED`, although that flag is set outside this file.

## Risks And Edge Cases
- Descriptor table ordering matters because `alg_find_test()` uses binary search; a misplaced or duplicate `.alg` silently risks missing or wrong tests, partially mitigated by `alg_check_test_descs_order()`.
- FIPS behavior is intentionally strict. A missing `fips_allowed` marker or failed test in FIPS mode can disable algorithms or panic the kernel.
- Scatterlist construction deliberately creates misalignment, page-boundary, split, in-place, and poison regions. Bugs in length rounding, offset adjustment, or poison checking can turn a test harness bug into false failures or missed memory corruption.
- Randomized full self-tests use non-cryptographic prandom data for speed and coverage, so failures can be data-shape dependent and may be hard to reproduce unless logs include enough configuration context.
- Generic implementation comparison assumes the generic driver exists and has matching public properties. Missing generic implementations are warnings, but mismatched digest/key/IV/block/auth sizes are hard failures.
- Some algorithms have `alg_test_null()` descriptors because they are aliases, hardware-key variants, or covered by another descriptor. That keeps registration possible but reduces direct coverage for those names.
- Request-structure integrity checks are valuable but can be brittle if crypto API semantics change to permit request mutation that was formerly forbidden.

## Test Signals
Strong signals include a kernel build with `CONFIG_CRYPTO_SELFTESTS=y`, crypto algorithm registration without `alg: self-tests ... failed` warnings, `/proc/crypto` showing expected algorithms as tested, and targeted `tcrypt` runs for affected algorithm names. Full coverage requires `CONFIG_CRYPTO_SELFTESTS_FULL=y` with `noslowtests=0` and enough `fuzz_iterations` to exercise random scatterlist, no-SIMD, import/export, generic-comparison, and inauthentic-AEAD paths.

Regression signals should include FIPS-mode boot or test runs for FIPS-allowed descriptors, allmodconfig/allyesconfig builds to compile conditional descriptor entries, and focused tests when adding vectors in `testmgr.h` or new entries in `alg_test_descs[]`. For failures, the harness logs algorithm family, driver, vector number or random vector name, configuration string, expected and actual errors, and hexdumps for wrong output.
