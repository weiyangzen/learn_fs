# sources/distributed-fs/ceph-client/lib/crypto/tests/sm3_kunit.c

Purpose: KUnit suite registration for SM3 hash correctness and optional benchmark coverage.

Important APIs/types/functions: maps the shared template to `sm3_ctx`, `sm3_init()`, `sm3_update()`, `sm3_final()`, and `SM3_DIGEST_SIZE`. It registers `sm3_test_cases[]` and `sm3_test_suite`.

Control flow: `HASH_KUNIT_CASES` from `hash-test-template.h` run the generated vector checks, followed by `benchmark_hash`. Module registration occurs through `kunit_test_suite(sm3_test_suite)`.

State and persistence: no local state; template lifecycle manages any shared test buffer.

Dependencies: `<crypto/sm3.h>`, generated `sm3-testvecs.h`, KUnit, and shared hash template.

Integration points: suite name `sm3`; validates the kernel crypto library SM3 implementation for consumers needing the Chinese SM3 hash algorithm.

Risks: coverage is generic and lacks SM3-specific named standard vectors in this file. Failures may need checking both generated vector provenance and implementation endian/padding logic.

Test signals: validates streaming hash behavior and benchmark path for SM3 across generated lengths.
