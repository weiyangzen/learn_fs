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
