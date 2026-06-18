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
