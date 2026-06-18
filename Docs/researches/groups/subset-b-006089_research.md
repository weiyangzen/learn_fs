# Research: subset-b-006089

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/curve25519_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/curve25519_kunit.c

## Purpose
This file defines the KUnit coverage and optional benchmark for the kernel Curve25519 library API. It validates scalar multiplication against a large in-file table of known-answer and edge-case vectors, checks that public-key generation is equivalent to multiplication by the X25519 basepoint, and reports throughput when `CONFIG_CRYPTO_LIB_BENCHMARK` is enabled.

## Important APIs, Types, and Functions
- `struct curve25519_test_vector` stores a 32-byte private scalar, 32-byte public input, 32-byte expected result, and `valid` boolean return expectation.
- `curve25519_test_vectors[]` contains 81 vectors: 65 expected-success vectors and 16 expected-failure vectors. The table covers RFC-style known answers, all-zero and low-order public inputs, boundary encodings near `p`, high-bit variants, and random-looking regression vectors.
- `test_curve25519()` iterates over every vector, calls `curve25519(out, vec->private, vec->public)`, and compares both the boolean return and output buffer against the vector.
- `test_curve25519_basepoint()` generates five random private keys, compares `curve25519_generate_public(out, in)` with `curve25519(out2, in, { 9 })`, and expects identical return values and outputs.
- `benchmark_curve25519()` uses the first vector, warms up 5000 operations, times 1024 operations under `preempt_disable()`, checks all operations succeeded, and prints operations per second.
- The KUnit suite registers `test_curve25519`, `test_curve25519_basepoint`, and `benchmark_curve25519` under suite name `curve25519`.

## Control Flow
The table-driven test is a straight loop over `curve25519_test_vectors[]`. Each iteration zero-initializes `out`, runs the scalar multiplication, then uses `KUNIT_EXPECT_EQ_MSG` and `KUNIT_EXPECT_MEMEQ_MSG`; failures are attributed to the vector index. The basepoint test is randomized but deterministic in behavior: each iteration obtains random bytes, computes the generated public key, computes multiplication by the conventional basepoint byte array `{ 9 }`, then compares both result and return flag. The benchmark first skips unless benchmarking is enabled, then separates warm-up from timed measurement.

## State and Persistence Behavior
There is no persistent state. Test vectors are static read-only data in the module. Per-test stack buffers hold private/public/output material. Random input is supplied through `get_random_bytes()` only for the basepoint equivalence test. Benchmark timing is transient and emitted through `kunit_info()`.

## Dependencies and Integration Points
The suite depends on `<crypto/curve25519.h>` for `CURVE25519_KEY_SIZE`, `curve25519()`, and `curve25519_generate_public()`, on KUnit for assertions and suite registration, and on timekeeping/preemption helpers for benchmarking. It integrates into kernel test discovery via `kunit_test_suite(curve25519_test_suite)` and into benchmark policy via `CONFIG_CRYPTO_LIB_BENCHMARK`.

## Risks and Edge Cases
The main risk is fixture correctness: the large inline table is the oracle for both success and failure cases, so a bad vector can encode an incorrect contract. The randomized basepoint test is a consistency test rather than an independent oracle, so it can miss defects shared by both public-key-generation and raw basepoint multiplication paths. The benchmark disables preemption during timing; it is gated, but slow or instrumented platforms may still show noisy measurements. The false-return vectors are important for rejecting all-zero/low-order or otherwise invalid shared secrets and should be preserved when refactoring the table.

## Test Signals
Strong signals include vector-indexed return-value checks, output digest checks for every vector, cross-API basepoint equivalence, and an optional performance signal. The suite does not test allocation failure or concurrency, because Curve25519 APIs are pure buffer operations in this context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/curve25519_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/ghash-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/ghash-testvecs.h

## Purpose
This generated header supplies GHASH known-answer fixtures for the shared hash KUnit template and GHASH-specific all-one-bits regression test. It turns deterministically generated inputs into compact oracles by storing input lengths and expected digests rather than the input bytes themselves.

## Important APIs, Types, and Data
- `hash_testvecs[]` is a static array of `{ size_t data_len; u8 digest[GHASH_DIGEST_SIZE]; }`.
- The vector lengths include empty input, small lengths 1-3, block and boundary lengths around 16/32/48/49/63/64/65/127/128/129, larger lengths 256/511/513/1000/3333/4096/4128/4160/4224, and the template maximum of 16384.
- `hash_testvec_consolidated[GHASH_DIGEST_SIZE]` is the expected digest of the concatenated digests for all lengths 0 through 4096 in the shared template.
- `ghash_allones_hashofhashes[GHASH_DIGEST_SIZE]` is the expected result for the GHASH all-one-bits key/message stress path in `ghash_kunit.c`.

## Control Flow
The header has no functions. It is included after `GHASH_DIGEST_SIZE` is visible and before `hash-test-template.h` is included by the GHASH suite. The template reads `hash_testvecs[]` for known-answer checks and `hash_testvec_consolidated` for exhaustive-length consolidation.

## State and Persistence Behavior
All state is static const test data. It has no runtime mutation and no persistence beyond the loaded KUnit module.

## Dependencies and Integration Points
The header depends on GHASH digest-size definitions from `<crypto/gf128hash.h>` and on the shared variable names expected by `hash-test-template.h`. It also integrates with `test_ghash_allones_key_and_message()` through the `ghash_allones_hashofhashes` symbol.

## Risks and Edge Cases
Because inputs are regenerated from length-derived seeds by the template, this file depends on the generator algorithm and the template PRNG staying aligned. A mismatch between `GHASH_DIGEST_SIZE` and the actual digest size would be caught at compile time or KUnit comparison time. The all-one-bits oracle is important for carryless-multiplication implementations that use standard multiplication emulation and can overflow.

## Test Signals
The header feeds known-answer checks, exhaustive length checks up to 4096, boundary-length coverage, maximum-buffer coverage at 16384 bytes, and the all-one-bits regression signal in the GHASH suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/ghash-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/ghash_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/ghash_kunit.c

## Purpose
This file adapts the keyed GHASH API to the shared hash test template, then adds GHASH-specific checks for prepared-key safety, alignment, all-one-bits arithmetic stress, interrupt-context key preparation, and optional throughput benchmarking.

## Important APIs, Types, and Functions
- `static struct ghash_key test_key` is the fixed suite key used to present GHASH as an unkeyed hash to `hash-test-template.h`.
- `ghash_init_withtestkey()` and `ghash_withtestkey()` wrap `ghash_init()` and `ghash()` using `test_key`.
- The template macros bind `HASH`, `HASH_CTX`, `HASH_SIZE`, `HASH_INIT`, `HASH_UPDATE`, and `HASH_FINAL` to GHASH wrappers and context types.
- `test_ghash_allones_key_and_message()` prepares an all-ones key, hashes all-ones messages from 0 to 4096 bytes in 16-byte steps, hashes those hashes, and compares to `ghash_allones_hashofhashes`.
- `check_key_consistency()` verifies two prepared keys are byte-identical and produce matching hashes over random lengths up to `MAX_LEN_FOR_KEY_CHECK`.
- `test_ghash_with_guarded_key()` checks `ghash_preparekey()` does not overread raw keys or prepared-key output when either ends at the guard page.
- `test_ghash_with_minimally_aligned_key()` verifies `struct ghash_key` only requires its declared alignment, not a stronger vector alignment.
- `test_ghash_preparekey_in_irqs()` uses `kunit_run_irq_test()` to confirm `ghash_preparekey()` gives the same prepared key when called from task, softirq, and hardirq-like contexts.
- `ghash_suite_init()` seeds and prepares `test_key`, then delegates shared guarded-buffer setup to `hash_suite_init()`.

## Control Flow
Suite initialization prepares the fixed test key from deterministic random bytes and allocates the shared guarded test buffer. Template-generated cases then run known-answer, all-length, incremental, guard-page, overlap, alignment, zeroization, IRQ, and benchmark tests. GHASH-specific cases run after the template cases and before benchmark. Suite exit frees the guarded buffer through `hash_suite_exit()`.

## State and Persistence Behavior
The only suite state is `test_key` plus the shared `test_buf`, `orig_test_buf`, and deterministic `random_seed` from `hash-test-template.h`. State is initialized once per suite and released at suite exit. No persistent filesystem or cross-module state exists.

## Dependencies and Integration Points
The file depends on `<crypto/gf128hash.h>`, `ghash-testvecs.h`, `hash-test-template.h`, KUnit, `vmalloc()` guard-page behavior from the template, and `kunit_run_irq_test()` from the template include path. It registers KUnit suite name `ghash`.

## Risks and Edge Cases
The test intentionally relies on bytewise equality of prepared keys; architecture-specific implementations must produce canonical prepared-key layouts, not just equivalent behavior. Guarded-buffer tests catch overreads only at the end boundary used by the template. The IRQ test is a strong signal for FPU/vector-state handling, but it only checks preparation output equality, not full GHASH execution in every context.

## Test Signals
Signals include generic hash API behavior from the shared template, GHASH vector oracles, all-one-bits overflow stress, guard-page key overread detection, minimal-alignment verification, interrupt-context key preparation, and optional benchmark throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/ghash_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/hash-test-template.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/hash-test-template.h

## Purpose
This header is a reusable KUnit test and benchmark template for kernel hash-like APIs. Including suites define macros for one-shot hash, context type, digest size, init/update/final functions, and optionally HMAC functions. The template then emits common test functions, suite init/exit helpers, case macros, deterministic test data generation, guard-page safety checks, interrupt-context checks, and a gated benchmark.

## Important APIs, Types, and Functions
- Required macros: `HASH`, `HASH_CTX`, `HASH_SIZE`, `HASH_INIT`, `HASH_UPDATE`, and `HASH_FINAL`.
- Optional HMAC macros: `HMAC_KEY`, `HMAC_CTX`, `HMAC_PREPAREKEY`, `HMAC_INIT`, `HMAC_UPDATE`, `HMAC_FINAL`, `HMAC`, and `HMAC_USINGRAWKEY`.
- `TEST_BUF_LEN` is 16384, and `test_buf` is positioned so `&test_buf[TEST_BUF_LEN]` is unmapped when `vmalloc()` provides a guard page after a page-aligned allocation.
- The deterministic PRNG is `rand32()` with a hard-coded linear congruential generator, plus helpers `rand_bytes()`, `rand_bytes_seeded_from_len()`, `rand_bool()`, `rand_length()`, and `rand_offset()`.
- `hash_suite_init()` allocates the guarded buffer; `hash_suite_exit()` frees it.
- Generic tests include `test_hash_test_vectors`, `test_hash_all_lens_up_to_4096`, `test_hash_incremental_updates`, `test_hash_buffer_overruns`, `test_hash_overlaps`, `test_hash_alignment_consistency`, `test_hash_ctx_zeroization`, `test_hash_interrupt_context_1`, and `test_hash_interrupt_context_2`.
- `test_hmac()` is emitted only when `HMAC` is defined and checks raw/prepared key consistency, consolidated HMAC output, and HMAC context zeroization.
- `UNKEYED_HASH_KUNIT_CASES` and `HASH_KUNIT_CASES` expose the generated cases to including suites.
- `benchmark_hash()` measures throughput for selected lengths when `CONFIG_CRYPTO_LIB_BENCHMARK` is enabled.

## Control Flow
Including suites define algorithm-specific macros and include this header. The suite calls `hash_suite_init()` before cases and `hash_suite_exit()` afterward. Vector tests generate seeded data based on vector length, run one-shot hash, and compare against `hash_testvecs[]`. Exhaustive-length testing hashes every length from 0 to 4096 and then hashes the digest stream. Incremental tests split random inputs into random update sequences and compare to one-shot output. Guard tests place data, digest output, or context at the end of the guarded allocation. Overlap tests intentionally alias output with the input region and mutate input after update. IRQ tests use `kunit_run_irq_test()` to run hash operations and incremental state transitions concurrently across task/softirq/hardirq contexts. Benchmarking warms up and then times selected lengths under `preempt_disable()`.

## State and Persistence Behavior
The template owns static globals `test_buf`, `orig_test_buf`, and `random_seed` in each translation unit that includes it. The buffer is allocated at suite init and freed at suite exit. The PRNG state is deterministic but mutable throughout tests; it is reset by length-seeded helper calls for vector-style tests. No persistent state crosses module unload/reload.

## Dependencies and Integration Points
The template depends on KUnit assertions, `kunit_run_irq_test()`, `vmalloc()`/`vfree()`, page-size/rounding helpers, atomics, preemption/timing helpers available through included kernel headers, and algorithm-specific vector symbols `hash_testvecs`, `hash_testvec_consolidated`, and optionally `hmac_testvec_consolidated`. It is consumed by MD5, SHA-1, SHA-224, GHASH, POLYVAL, and Poly1305 suites in this subset.

## Risks and Edge Cases
The header emits static symbols, so it must be included in only one suite translation unit per macro configuration. Template users must ensure `HASH_FINAL` zeroizes the context if they opt into the generic zeroization test. The guard-page assumption relies on the vmalloc allocation layout described in the comments. The deterministic PRNG is intentionally non-cryptographic; changing it breaks generated test-vector compatibility. The IRQ tests assume `IRQ_TEST_NUM_BUFFERS` matches `kunit_run_irq_test()` max concurrency. `test_hmac()` uses one consolidated oracle, which gives broad coverage but does not identify the exact failing data/key length.

## Test Signals
This template supplies broad behavior signals: known-answer correctness, exhaustive small-length coverage, incremental equivalence, data/output/context overrun checks, output-input aliasing, post-update input independence, alignment consistency, context zeroization, interrupt-context safety, HMAC wrapper correctness, and optional throughput measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/hash-test-template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/md5-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/md5-testvecs.h

## Purpose
This generated header provides MD5 and HMAC-MD5 oracle data for `hash-test-template.h`. It stores expected MD5 digests for deterministic length-seeded inputs plus consolidated digest values for exhaustive MD5 and HMAC coverage.

## Important APIs, Types, and Data
- `hash_testvecs[]` contains `{ data_len, digest[MD5_DIGEST_SIZE] }` entries.
- Length coverage spans empty input, small inputs, block-boundary lengths around the 64-byte MD5 block size, larger non-boundary inputs, values just above 4096, and 16384.
- `hash_testvec_consolidated[MD5_DIGEST_SIZE]` is the expected hash of hashes for all lengths 0 through 4096.
- `hmac_testvec_consolidated[MD5_DIGEST_SIZE]` is the expected consolidated HMAC result over all data lengths 0 through 4096 and cycling key lengths up to 292 as implemented by the template.

## Control Flow
The header contributes data only. `md5_kunit.c` includes it before `hash-test-template.h`, which then reads the symbols during MD5 and HMAC-MD5 tests.

## State and Persistence Behavior
All data is `static const` in the including translation unit. There is no mutation or persistence.

## Dependencies and Integration Points
The header depends on `MD5_DIGEST_SIZE` from `<crypto/md5.h>` and on the shared symbol names expected by `hash-test-template.h`. It is generated by `./scripts/crypto/gen-hash-testvecs.py md5`, so generator/template PRNG compatibility is part of the contract.

## Risks and Edge Cases
MD5 is cryptographically obsolete for collision resistance, but these tests validate implementation compatibility and HMAC behavior, not security suitability. The fixtures are compact; incorrect PRNG seeding or generator drift would cause broad failures. The consolidated HMAC value localizes failures poorly but gives dense coverage.

## Test Signals
The data drives known-answer MD5 checks, all-length MD5 consolidation, and HMAC-MD5 raw/prepared-key consistency plus consolidated output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/md5-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/md5_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/md5_kunit.c

## Purpose
This file instantiates the shared hash test template for the kernel MD5 and HMAC-MD5 library APIs. It provides no algorithm-specific tests beyond the template cases and optional benchmark.

## Important APIs, Types, and Functions
- Includes `<crypto/md5.h>` and `md5-testvecs.h`.
- Maps `HASH` to `md5`, `HASH_CTX` to `md5_ctx`, `HASH_SIZE` to `MD5_DIGEST_SIZE`, and init/update/final macros to `md5_init`, `md5_update`, and `md5_final`.
- Maps HMAC macros to `hmac_md5_key`, `hmac_md5_ctx`, `hmac_md5_preparekey`, `hmac_md5_init`, `hmac_md5_update`, `hmac_md5_final`, `hmac_md5`, and `hmac_md5_usingrawkey`.
- Includes `hash-test-template.h` to generate the actual tests.
- Registers `HASH_KUNIT_CASES` and `benchmark_hash` in suite name `md5`.

## Control Flow
At compile time, macros specialize the template. At runtime, `hash_suite_init()` allocates the guarded buffer, the template cases validate MD5 and HMAC-MD5 behavior, `benchmark_hash()` runs only when enabled, and `hash_suite_exit()` frees the guarded buffer.

## State and Persistence Behavior
State comes from the template: static guarded buffer pointers and deterministic random seed. MD5/HMAC contexts are per-test stack variables and are expected to be zeroized on finalization by the generic tests.

## Dependencies and Integration Points
The suite integrates with KUnit under suite name `md5`, with the crypto library through `<crypto/md5.h>`, and with test fixtures from `md5-testvecs.h`. `CONFIG_CRYPTO_LIB_BENCHMARK` controls benchmark execution.

## Risks and Edge Cases
Because this file is a pure template instantiation, most behavioral risk is in macro mapping correctness. A wrong macro could make tests exercise a different path or mis-size buffers. The suite assumes MD5 finalization and HMAC finalization zeroize contexts as required by the template.

## Test Signals
Signals include MD5 known answers, exhaustive lengths through 4096, incremental equivalence, guard-page overrun detection, overlap and alignment behavior, context zeroization, interrupt-context safety, HMAC-MD5 consolidated correctness, and optional throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/md5_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/mldsa-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/mldsa-testvecs.h

## Purpose
This header provides ML-DSA verification known-answer fixtures extracted from leancrypto. It defines a shared vector struct and one valid signature/public-key/message tuple for each supported parameter set: ML-DSA-44, ML-DSA-65, and ML-DSA-87.

## Important APIs, Types, and Data
- `struct mldsa_testvector` stores `enum mldsa_alg alg`, signature length, message length, public-key length, and pointers to signature, message, and public key byte arrays.
- `mldsa44_testvector`, `mldsa65_testvector`, and `mldsa87_testvector` each contain inline compound-literal byte arrays sized with the corresponding public-key and signature constants.
- Each vector uses a 64-byte message (`.msg_len = 64`) and parameter-specific `.pk_len` and `.sig_len` constants.
- The header uses `MLDSA44_PUBLIC_KEY_SIZE`, `MLDSA44_SIGNATURE_SIZE`, `MLDSA65_*`, and `MLDSA87_*` constants from `<crypto/mldsa.h>` through the including C file.

## Control Flow
The header has no executable code. `mldsa_kunit.c` includes it after defining parameter metadata, then passes each vector to common verification, mutation, malformed-signature, and benchmark helpers.

## State and Persistence Behavior
All fixtures are static const objects and immutable byte arrays in the test module. There is no runtime state and no persistence beyond the loaded module.

## Dependencies and Integration Points
The data integrates directly with `mldsa_verify()` tests in `mldsa_kunit.c`. It depends on ML-DSA enum and size constants, and on the signature encoding layout expected by the verifier and the negative tests: `ctilde || z || h`.

## Risks and Edge Cases
The negative tests in `mldsa_kunit.c` assume structural properties of these valid signatures, including enough nonzero hints for swapping and fewer than `omega` nonzero hints for extra-index testing. If vectors are replaced, those assumptions must be revalidated. Since only one valid vector per parameter set is present, this header is a correctness anchor but not exhaustive coverage of signature distributions.

## Test Signals
The vectors support positive verification for all three security levels, length validation, malformed `z` coefficient checks, malformed hint-vector checks, random bit mutation rejection, and benchmark measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/mldsa-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/mldsa_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/mldsa_kunit.c

## Purpose
This file defines KUnit tests and optional benchmarks for ML-DSA signature verification. It validates known-good signatures for ML-DSA-44, ML-DSA-65, and ML-DSA-87, checks exact rejection modes for malformed encodings and altered inputs, verifies an exported `mldsa_use_hint()` helper against a reference translation of FIPS 204, and measures verification throughput when enabled.

## Important APIs, Types, and Functions
- `params[]` records per-algorithm signature length, public-key length, `k`, `lambda`, `gamma1`, `beta`, and `omega`.
- `do_mldsa_and_assert_success()` calls `mldsa_verify()` and expects success.
- `kunit_kmemdup_or_fail()` allocates mutable copies of fixture data under KUnit ownership.
- `test_mldsa_z_range()` mutates the first packed `z` coefficient and expects `-EBADMSG` for out-of-range coefficients and `-EKEYREJECTED` for in-range but incorrect coefficients.
- `test_mldsa_bad_hints()` mutates the encoded hint vector and expects `-EBADMSG` for cumulative count overflow, decreasing counts, unsorted indices, and extra indices.
- `test_mldsa_mutation()` randomly flips 200 bits each in signature, message, and public key copies and expects every mutation to make verification fail, then verifies all changes were undone.
- `test_mldsa()` combines valid verification, exact signature/public-key length failures, message-short failure, `z` tests, hint tests, and mutation tests for one vector.
- `mod()`, `symmetric_mod()`, `decompose_ref()`, and `use_hint_ref()` implement a simple reference path for FIPS 204 `Decompose` and `UseHint`.
- `test_mldsa_use_hint()` exhaustively compares `mldsa_use_hint()` for both supported `gamma2` forms, both hint bits, and every `r` in `[0, Q)`.
- `benchmark_mldsa()` warms up and times `mldsa_verify()` for a vector when `CONFIG_CRYPTO_LIB_BENCHMARK` is enabled.

## Control Flow
The suite registers per-parameter test wrappers, the exhaustive `UseHint` test, and per-parameter benchmarks. Each parameter wrapper calls `test_mldsa()`, which first asserts vector sizes and success, then validates malformed length behavior, then runs structured corruption tests and randomized mutation tests. The helper test loops over all possible `r` values for each `gamma2` choice and compares the implementation to reference arithmetic. Benchmarks are skipped unless enabled.

## State and Persistence Behavior
Fixtures are static const from `mldsa-testvecs.h`. Mutable copies are allocated through KUnit for negative tests and automatically cleaned with the test context. Random mutation positions come from `get_random_u32_below()`, so exact mutated positions vary by run, but the contract is invariant. No persistent state is created.

## Dependencies and Integration Points
The file depends on `<crypto/mldsa.h>` for `mldsa_verify()`, `mldsa_use_hint()`, algorithm constants, and namespace-exported internals; KUnit for assertions; `<linux/random.h>` for mutation sampling; and `<linux/unaligned.h>` for packed coefficient editing. `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")` is required for the helper under test.

## Risks and Edge Cases
The test suite is verification-only; it does not cover ML-DSA signing or key generation. Random mutation testing can miss specific bit positions on a given run, though 200 iterations per input class give useful regression coverage. Exact errno assertions are valuable but couple tests to verifier error taxonomy. The exhaustive `UseHint` loop is large and may be slow on debug builds. The signature-layout tests assume `ctilde || z || h` and must be updated if encoding changes.

## Test Signals
Strong signals include known-good verification for all supported parameter sets, strict length rejection, malformed-encoding errno checks, randomized tamper rejection for signatures/messages/public keys, exhaustive helper equivalence to FIPS 204 pseudocode, and optional verification throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/mldsa_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/nh-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/nh-testvecs.h

## Purpose
This generated header supplies a fixed NH key, fixed message, and expected NH outputs for selected message lengths. It is the oracle data for the compact NH KUnit suite.

## Important APIs, Types, and Data
- `nh_test_key[NH_KEY_BYTES]` is the test key byte array.
- `nh_test_msg[NH_MESSAGE_BYTES]` is the input message byte array.
- `nh_test_val16`, `nh_test_val96`, `nh_test_val256`, and `nh_test_val1024` are expected `NH_HASH_BYTES` outputs for the corresponding message lengths.
- The data is generated by `./scripts/crypto/gen-hash-testvecs.py nh`.

## Control Flow
The header contains data only. `nh_kunit.c` copies and endian-converts the key, then invokes `nh()` with lengths 16, 96, 256, and 1024 and compares against the four expected outputs.

## State and Persistence Behavior
All arrays are static const and immutable. There is no runtime state.

## Dependencies and Integration Points
The header depends on NH size constants from `<crypto/nh.h>` and integrates only with `nh_kunit.c`. The KUnit runner relies on the message array being large enough for the 1024-byte test and the key array matching `NH_KEY_WORDS` after little-endian conversion.

## Risks and Edge Cases
Coverage is narrower than the shared hash template: it checks selected lengths only and does not test incremental behavior, alignment, guard pages, or IRQ context. The key endianness contract is explicit in the consumer, so changing key representation in the NH API would require test updates.

## Test Signals
The header provides known-answer signals at four lengths, including a very small input, a medium input, and the full 1024-byte generated message used by the suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/nh-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/nh_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/nh_kunit.c

## Purpose
This file defines a focused KUnit known-answer test for the NH hash primitive. It validates the `nh()` implementation at four message lengths using generated fixtures from `nh-testvecs.h`.

## Important APIs, Types, and Functions
- `test_nh()` allocates a mutable `u32` key buffer of `NH_KEY_BYTES`, copies `nh_test_key`, converts it from little-endian words with `le32_to_cpu_array()`, and hashes `nh_test_msg`.
- The output buffer is `__le64 hash[NH_NUM_PASSES]`, matching NH's little-endian output representation.
- The test calls `nh(key, nh_test_msg, 16/96/256/1024, hash)` and compares with `KUNIT_ASSERT_MEMEQ()`.
- The suite registers a single case under suite name `nh`.

## Control Flow
KUnit invokes `test_nh()`. The test allocates key memory, asserts allocation success, prepares host-order key words, runs four one-shot calls, and aborts on the first mismatch due to `KUNIT_ASSERT_MEMEQ`.

## State and Persistence Behavior
The only dynamic state is KUnit-owned key allocation and a stack output buffer. Static fixture data remains read-only. No persistent or global mutable state is used.

## Dependencies and Integration Points
The file depends on `<crypto/nh.h>` for `nh()`, constants, and types; KUnit for allocation/assertions; endian helper `le32_to_cpu_array()` through kernel headers; and `nh-testvecs.h` for fixtures. It registers via `kunit_test_suite(nh_test_suite)`.

## Risks and Edge Cases
The test does not exercise alignment variants, invalid lengths, buffer boundaries, or concurrency. It assumes `nh()` receives host-order key words while vectors are stored as little-endian bytes. The fixture set is small but covers multiple lengths including full generated-message size.

## Test Signals
The suite gives direct known-answer signals for NH at 16, 96, 256, and 1024 bytes and catches key-endian conversion regressions in the test path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/nh_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/poly1305-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/poly1305-testvecs.h

## Purpose
This generated header supplies Poly1305 known-answer fixtures for the shared hash template and a Poly1305-specific all-one-bits regression oracle. Like the other generated hash vector headers, it stores expected outputs for deterministic length-seeded inputs rather than storing all input data.

## Important APIs, Types, and Data
- `hash_testvecs[]` contains `{ data_len, digest[POLY1305_DIGEST_SIZE] }` entries.
- Lengths include empty input, short lengths, Poly1305 block boundaries and near-boundaries, larger sizes, and the template maximum of 16384.
- `hash_testvec_consolidated[POLY1305_DIGEST_SIZE]` is the expected digest of digest stream for lengths 0 through 4096 under the fixed suite key.
- `poly1305_allones_macofmacs[POLY1305_DIGEST_SIZE]` is the expected output for the long-running all-one-bits MAC-of-MACs stress test.

## Control Flow
The header has no functions. `poly1305_kunit.c` includes it, then the shared template consumes `hash_testvecs` and `hash_testvec_consolidated`, while the Poly1305-specific test consumes `poly1305_allones_macofmacs`.

## State and Persistence Behavior
All data is static const and immutable.

## Dependencies and Integration Points
The header depends on `POLY1305_DIGEST_SIZE` and related constants from `<crypto/poly1305.h>` via the including C file. It is generated by `./scripts/crypto/gen-hash-testvecs.py poly1305`, and its compact-input model depends on the shared template PRNG.

## Risks and Edge Cases
Poly1305 is keyed, so vector interpretation depends on the suite's deterministic `test_key` generation staying aligned with the generator. The all-one-bits oracle is especially important for accumulator overflow and final reduction regressions.

## Test Signals
The data drives known-answer checks, exhaustive length consolidation, and the all-one-bits MAC-of-MACs stress test used to catch rare reduction/carry bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/poly1305-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/poly1305_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/poly1305_kunit.c

## Purpose
This file adapts the keyed Poly1305 API to the shared hash test template and adds Poly1305-specific regression tests for all-one-bits accumulator stress and modular reduction edge cases.

## Important APIs, Types, and Functions
- `static u8 test_key[POLY1305_KEY_SIZE]` is the deterministic suite key.
- Local helper `poly1305()` provides a one-shot wrapper around `poly1305_init()`, `poly1305_update()`, and `poly1305_final()`.
- `poly1305_init_withtestkey()` and `poly1305_withtestkey()` adapt the keyed API to the template macros.
- `poly1305_suite_init()` fills `test_key` using `rand_bytes_seeded_from_len()` and then calls `hash_suite_init()`.
- `test_poly1305_allones_keys_and_message()` initializes two Poly1305 contexts with all-one-bits key data, repeatedly updates a long-running MAC context with all-one-bits messages of lengths 0..4096 in 16-byte steps over 32 rounds, feeds each temporary MAC into a MAC-of-MACs context, and compares the final result to `poly1305_allones_macofmacs`.
- `test_poly1305_reduction_edge_cases()` uses `r_key=1`, `s_key=0`, and crafted three-block messages near the `2^130 - 5` modulus boundary to check final modular reduction.

## Control Flow
Suite init seeds the fixed key and guarded buffer. Template-generated tests run first through `HASH_KUNIT_CASES`. Poly1305-specific tests then exercise carry/reduction stress before `benchmark_hash()`. Suite exit frees the template buffer.

## State and Persistence Behavior
The suite key is static mutable state initialized once per suite. The shared guarded buffer and PRNG state come from the template. Poly1305 contexts are stack locals except for copied temporary context snapshots in the all-one-bits test. No persistent state exists.

## Dependencies and Integration Points
The file depends on `<crypto/poly1305.h>`, `poly1305-testvecs.h`, and `hash-test-template.h`. It registers the KUnit suite name `poly1305` and uses the template benchmark gate `CONFIG_CRYPTO_LIB_BENCHMARK`.

## Risks and Edge Cases
The one-shot helper is local because the API apparently lacks a direct one-shot function; if the library later adds one, tests may need to ensure both paths match. The all-one-bits stress intentionally mutates cumulative context over many updates, so it is sensitive to any change in Poly1305 update/final semantics. The reduction edge test covers small `i` values near the modulus boundary, not every possible boundary case.

## Test Signals
Signals include generic hash-template coverage, deterministic Poly1305 vectors, all-one-bits key/message accumulator stress, explicit modular reduction edge cases, zeroization/overlap/alignment/IRQ signals from the template, and optional throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/poly1305_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/polyval-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/polyval-testvecs.h

## Purpose
This generated header supplies POLYVAL known-answer fixtures for the shared hash template and an all-one-bits regression oracle for POLYVAL arithmetic.

## Important APIs, Types, and Data
- `hash_testvecs[]` contains `{ data_len, digest[POLYVAL_DIGEST_SIZE] }` entries.
- Length coverage mirrors the other generated hash-vector headers: short inputs, block and near-block lengths, larger inputs, values around 4096, and 16384.
- `hash_testvec_consolidated[POLYVAL_DIGEST_SIZE]` is the expected hash-of-hashes for all lengths 0 through 4096.
- `polyval_allones_hashofhashes[POLYVAL_DIGEST_SIZE]` is the expected result for the all-one-bits key/message stress test.

## Control Flow
The header is included by `polyval_kunit.c`. The shared template reads `hash_testvecs` and `hash_testvec_consolidated`; the POLYVAL-specific all-one-bits test reads `polyval_allones_hashofhashes`.

## State and Persistence Behavior
All arrays are static const data with no mutation or persistence.

## Dependencies and Integration Points
The data depends on POLYVAL constants from `<crypto/gf128hash.h>` and the shared generated-vector PRNG contract. It integrates with both `hash-test-template.h` and `test_polyval_allones_key_and_message()`.

## Risks and Edge Cases
Because POLYVAL is related to GHASH but uses different bit/byte ordering conventions, fixture correctness is critical. The generated vectors and the explicit RFC 8452 test in the C file together help detect accidental GHASH/POLYVAL endianness substitution.

## Test Signals
The header drives known-answer vectors, exhaustive length consolidation through 4096, maximum-buffer coverage, and all-one-bits arithmetic stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/polyval-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/polyval_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/polyval_kunit.c

## Purpose
This file adapts keyed POLYVAL to the shared hash template and adds POLYVAL-specific checks for RFC 8452 compatibility, all-one-bits arithmetic stress, key preparation safety, prepared-key alignment, interrupt-context key preparation, and optional benchmarking.

## Important APIs, Types, and Functions
- `static struct polyval_key test_key` is the fixed suite key used by template wrappers.
- `polyval_init_withtestkey()` and `polyval_withtestkey()` wrap `polyval_init()` and `polyval()`.
- The template macros bind POLYVAL functions and context types to `hash-test-template.h`.
- `test_polyval_rfc8452_testvec()` verifies a concrete AES-GCM-SIV/POLYVAL example from RFC 8452.
- `test_polyval_allones_key_and_message()` mirrors the GHASH all-one-bits stress path with POLYVAL functions and compares to `polyval_allones_hashofhashes`.
- `check_key_consistency()` verifies byte-identical prepared keys and equal hashes over random lengths.
- `test_polyval_with_guarded_key()` catches overreads of raw key or prepared-key output near the guard page.
- `test_polyval_with_minimally_aligned_key()` verifies only `__alignof__(struct polyval_key)` is required.
- `test_polyval_preparekey_in_irqs()` checks `polyval_preparekey()` consistency in task/softirq/hardirq-like contexts.
- `polyval_suite_init()` prepares the deterministic suite key and allocates the shared guarded buffer.

## Control Flow
Suite init prepares the key from deterministic random bytes and delegates buffer setup to the template. Generated template cases run first, followed by RFC compatibility, all-one-bits, guarded-key, alignment, IRQ key-preparation, and benchmark cases. Suite exit calls `hash_suite_exit()`.

## State and Persistence Behavior
Suite state consists of `test_key` plus the template's guarded buffer and PRNG state. Test-specific keys, contexts, and hashes are stack locals. There is no persistence.

## Dependencies and Integration Points
The file depends on `<crypto/gf128hash.h>`, `polyval-testvecs.h`, `hash-test-template.h`, KUnit, guarded vmalloc behavior through the template, and `kunit_run_irq_test()` through the template. It registers KUnit suite name `polyval`.

## Risks and Edge Cases
The RFC vector is a high-value compatibility check because POLYVAL endianness mistakes can still produce internally consistent template results if fixtures were wrong. The prepared-key equality assumption requires canonical key layout across implementations. Guard and minimal-alignment tests cover specific placements, not every possible unaligned address or vector backend.

## Test Signals
Signals include shared hash-template behavior, generated POLYVAL vector oracles, RFC 8452 compatibility, all-one-bits overflow stress, key overread detection, key alignment validation, interrupt-context preparekey consistency, and optional throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/polyval_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha1-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha1-testvecs.h

## Purpose
This generated header supplies SHA-1 and HMAC-SHA1 expected outputs for the shared hash test template. It compactly represents deterministic input data through lengths and stores the corresponding digest or consolidated digest results.

## Important APIs, Types, and Data
- `hash_testvecs[]` contains `{ data_len, digest[SHA1_DIGEST_SIZE] }` entries.
- Lengths cover empty input, short inputs, block-boundary lengths around 64 bytes, larger values, values around 4096, and 16384.
- `hash_testvec_consolidated[SHA1_DIGEST_SIZE]` is the expected hash-of-hashes for all lengths 0 through 4096.
- `hmac_testvec_consolidated[SHA1_DIGEST_SIZE]` is the expected consolidated HMAC result over the template's data/key length sweep.

## Control Flow
The header defines data only. `sha1_kunit.c` includes it before the template, and the template consumes the symbols in generated test cases.

## State and Persistence Behavior
All arrays are static const and immutable.

## Dependencies and Integration Points
The header depends on `SHA1_DIGEST_SIZE` from `<crypto/sha1.h>` and the shared template's symbol naming contract. It is generated by `./scripts/crypto/gen-hash-testvecs.py sha1`.

## Risks and Edge Cases
SHA-1 is not collision-resistant for modern security uses, but these tests validate compatibility and implementation behavior. Generator/template PRNG drift would invalidate all compact fixtures. Consolidated HMAC failure reports are intentionally broad rather than per-input.

## Test Signals
The data drives SHA-1 known-answer tests, exhaustive all-length validation through 4096, and HMAC-SHA1 raw/prepared-key consistency plus consolidated output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha1-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha1_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha1_kunit.c

## Purpose
This file instantiates the shared hash test template for kernel SHA-1 and HMAC-SHA1 APIs, registering the generated behavior tests and optional benchmark as a KUnit suite.

## Important APIs, Types, and Functions
- Includes `<crypto/sha1.h>` and `sha1-testvecs.h`.
- Maps `HASH` to `sha1`, `HASH_CTX` to `sha1_ctx`, `HASH_SIZE` to `SHA1_DIGEST_SIZE`, and init/update/final macros to `sha1_init`, `sha1_update`, and `sha1_final`.
- Maps HMAC macros to the `hmac_sha1_*` API family.
- Includes `hash-test-template.h` to emit test functions and `HASH_KUNIT_CASES`.
- Registers suite name `sha1` with template init/exit hooks and benchmark.

## Control Flow
The suite delegates all runtime logic to the template. Initialization allocates the guarded buffer, generated cases run SHA-1 and HMAC-SHA1 checks, benchmark runs only when enabled, and suite exit frees state.

## State and Persistence Behavior
State is limited to the template's static guarded buffer and PRNG seed plus per-test stack contexts. No persistent state is used.

## Dependencies and Integration Points
The file integrates with the kernel SHA-1 crypto library, KUnit, `sha1-testvecs.h`, and `CONFIG_CRYPTO_LIB_BENCHMARK`. It depends on the template zeroization expectations for finalization behavior.

## Risks and Edge Cases
Macro binding errors are the main local risk. Like MD5, SHA-1's security status does not affect the implementation-compatibility role of these tests. All detailed behavioral coverage comes from `hash-test-template.h`.

## Test Signals
Signals include SHA-1 known answers, exhaustive small-length coverage, incremental equivalence, guard-page safety, overlap/alignment behavior, context zeroization, interrupt-context safety, HMAC-SHA1 checks, and optional throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha1_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha224-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha224-testvecs.h

## Purpose
This generated header supplies SHA-224 and HMAC-SHA224 oracle data for the shared hash test template.

## Important APIs, Types, and Data
- `hash_testvecs[]` contains `{ data_len, digest[SHA224_DIGEST_SIZE] }` entries.
- The selected lengths exercise empty and small inputs, SHA-2 block boundaries and near-boundaries, larger deterministic inputs, values around 4096, and 16384.
- `hash_testvec_consolidated[SHA224_DIGEST_SIZE]` is the expected digest of the digest stream for every length 0 through 4096.
- `hmac_testvec_consolidated[SHA224_DIGEST_SIZE]` is the expected result of the template's consolidated HMAC sweep.

## Control Flow
The header contains only data. `sha224_kunit.c` includes it before `hash-test-template.h`, which consumes these symbols in generated cases.

## State and Persistence Behavior
All arrays are static const. There is no mutation or persistence.

## Dependencies and Integration Points
The header depends on `SHA224_DIGEST_SIZE` from `<crypto/sha2.h>` and the generator/template PRNG contract. It is generated by `./scripts/crypto/gen-hash-testvecs.py sha224`.

## Risks and Edge Cases
Fixture correctness depends on generator consistency. The compact representation does not show raw input bytes, so debugging a mismatch often requires regenerating the deterministic input for the failing length. HMAC coverage is broad but consolidated.

## Test Signals
The data drives SHA-224 known-answer checks, exhaustive length consolidation through 4096, and HMAC-SHA224 consistency and output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha224-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha224_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha224_kunit.c

## Purpose
This file instantiates the shared hash test template for SHA-224 and HMAC-SHA224, then registers the generated cases and optional benchmark as KUnit suite `sha224`.

## Important APIs, Types, and Functions
- Includes `<crypto/sha2.h>` and `sha224-testvecs.h`.
- Maps `HASH` to `sha224`, `HASH_CTX` to `sha224_ctx`, `HASH_SIZE` to `SHA224_DIGEST_SIZE`, and init/update/final macros to `sha224_init`, `sha224_update`, and `sha224_final`.
- Maps HMAC macros to the `hmac_sha224_*` API family.
- Includes `hash-test-template.h` and registers `HASH_KUNIT_CASES` plus `benchmark_hash`.

## Control Flow
All behavior is generated by the template after macro specialization. Suite initialization allocates guarded test storage, generated hash/HMAC tests execute, benchmark is skipped unless enabled, and suite exit frees the buffer.

## State and Persistence Behavior
State is the template-owned guarded buffer and PRNG seed, plus stack-local hash/HMAC contexts. There is no persistent state.

## Dependencies and Integration Points
The suite depends on the SHA-2 crypto header, KUnit, `sha224-testvecs.h`, the shared template, and benchmark gating through `CONFIG_CRYPTO_LIB_BENCHMARK`.

## Risks and Edge Cases
As with the other thin wrappers, the main local risk is incorrect macro mapping. The suite assumes SHA-224 finalization and HMAC finalization zeroize contexts. Algorithm-specific edge behavior beyond the template is not added here.

## Test Signals
Signals include SHA-224 known answers, exhaustive small-length coverage, incremental equivalence, buffer-overrun checks, overlap and alignment behavior, zeroization, interrupt-context safety, HMAC-SHA224 consolidated checks, and optional throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha224_kunit.c -->
