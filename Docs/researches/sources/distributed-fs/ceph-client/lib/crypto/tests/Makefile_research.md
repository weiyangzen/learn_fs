# sources/distributed-fs/ceph-client/lib/crypto/tests/Makefile

## Purpose

This Makefile maps crypto KUnit Kconfig symbols to test object files. It was read as a complete 18-line file.

## Important APIs, Types, and Functions

It adds objects such as `aes_cbc_macs_kunit.o`, `blake2b_kunit.o`, `blake2s_kunit.o`, `chacha20poly1305_kunit.o`, `curve25519_kunit.o`, `ghash_kunit.o`, hash KUnit objects, and SM3 tests based on `CONFIG_CRYPTO_LIB_*_KUNIT_TEST`.

## Control Flow

Kbuild includes each object when its corresponding config is built-in or modular. SHA-256 and SHA-512 options each build two test objects to cover the truncated and full variants.

## State and Persistence Behavior

There is no runtime state. Build output composition is determined by configuration.

## Dependencies and Integration Points

It integrates directly with `tests/Kconfig` and the KUnit source files in the same directory.

## Risks and Edge Cases

Missing object mappings make enabled tests disappear at build time. Grouped options must keep their object lists synchronized with the related Kconfig help text.

## Test Signals

KUnit build tests for each config symbol and build logs showing expected objects validate this file.
