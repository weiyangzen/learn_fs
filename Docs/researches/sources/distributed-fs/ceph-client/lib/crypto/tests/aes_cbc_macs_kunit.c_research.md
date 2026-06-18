# sources/distributed-fs/ceph-client/lib/crypto/tests/aes_cbc_macs_kunit.c

## Purpose

This KUnit suite tests AES-CMAC, AES-XCBC-MAC, and AES-CBC-MAC crypto library functions and includes optional benchmark coverage. It was read as a complete 228-line file.

## Important APIs, Types, and Functions

It defines `test_key`, wrapper functions `aes_cmac_init_withtestkey` and `aes_cmac_withtestkey`, suite init/exit, and tests `test_aes_cmac_rfc4493`, `test_aes_xcbcmac_rfc3566`, and `test_aes_cbcmac_rfc3610`. It uses `HASH_KUNIT_CASES` from `hash-test-template.h`.

## Control Flow

Suite init deterministically generates a 256-bit raw key, prepares `test_key`, and initializes shared hash test buffers. Template tests cover CMAC as a fixed-key hash. Additional tests verify RFC 4493 CMAC examples, RFC 3566 XCBC-MAC key preparation and MAC output, and RFC 3610-derived CBC-MAC data including incremental split updates and zero-padding behavior up to a block boundary.

## State and Persistence Behavior

`test_key` is static test-suite state. Per-test keys, contexts, and MAC buffers are stack-local. Shared test buffers are managed by the hash template suite init/exit.

## Dependencies and Integration Points

It depends on `<crypto/aes-cbc-macs.h>`, generated AES-CMAC vectors, KUnit, the shared hash template, and the CRYPTO_INTERNAL namespace.

## Risks and Edge Cases

The deterministic key must match generated vectors. CBC-MAC tests intentionally rely on trailing zero behavior, so regressions in padding or incremental update logic should be caught. Benchmark cases are gated by Kconfig.

## Test Signals

The suite itself is the signal: template vector passes, RFC example passes, split-update coverage, and benchmark execution when enabled.
