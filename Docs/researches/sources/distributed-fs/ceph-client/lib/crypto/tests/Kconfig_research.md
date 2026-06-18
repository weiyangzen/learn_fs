# sources/distributed-fs/ceph-client/lib/crypto/tests/Kconfig

## Purpose

This Kconfig file defines KUnit test options for kernel crypto library algorithms and an optional benchmark switch. It was read as a complete 184-line file.

## Important APIs, Types, and Functions

It declares tristate test options for AES-CBC-MAC family, BLAKE2b, BLAKE2s, ChaCha20Poly1305, Curve25519, GHASH, MD5, ML-DSA, NH, Poly1305, POLYVAL, SHA-1, SHA-256/SHA-224, SHA-512/SHA-384, SHA-3, and SM3. It also defines `CRYPTO_LIB_ENABLE_ALL_FOR_KUNIT`, `CRYPTO_LIB_BENCHMARK_VISIBLE`, and `CRYPTO_LIB_BENCHMARK`.

## Control Flow

Kconfig selection controls which KUnit object files are built. Most test options depend on KUNIT and the corresponding crypto library, default to `KUNIT_ALL_TESTS`, and select benchmark visibility. The enable-all option selects the library code needed by the tests without enabling every test directly.

## State and Persistence Behavior

There is no runtime state. Configuration state is persisted in kernel build configuration files.

## Dependencies and Integration Points

It integrates with `lib/crypto/tests/Makefile`, KUnit, and the crypto library Kconfig symbols. Benchmark visibility lets individual test suites include benchmark cases only when selected.

## Risks and Edge Cases

Dependency mistakes can make tests silently unavailable or pull in unwanted crypto code. BLAKE2s is special because it is always built for `/dev/random`, so its test does not depend on a `CRYPTO_LIB_BLAKE2S` option.

## Test Signals

`allnoconfig`/`allyesconfig`/KUnit build coverage, `KUNIT_ALL_TESTS`, and selective enabling of each symbol validate this file.
