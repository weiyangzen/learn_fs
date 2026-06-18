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
