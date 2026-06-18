# sources/distributed-fs/ceph-client/lib/crypto/tests/sha384_kunit.c

Purpose: minimal KUnit suite wiring for SHA-384 and HMAC-SHA384 using the shared hash test template.

Important APIs/types/functions: maps template macros to `sha384_ctx`, `sha384_init()`, `sha384_update()`, `sha384_final()`, `hmac_sha384_key`, `hmac_sha384_ctx`, `hmac_sha384_preparekey()`, `hmac_sha384_init()`, `hmac_sha384_update()`, `hmac_sha384_final()`, `hmac_sha384()`, and `hmac_sha384_usingrawkey()`. It registers `hash_test_cases[]` and `hash_test_suite`.

Control flow: compile-time macro binding causes `hash-test-template.h` to generate the standard tests and benchmark function. Runtime suite execution runs `HASH_KUNIT_CASES`, then `benchmark_hash` when benchmarks are enabled by the template/config.

State and persistence: no local mutable state. Suite lifecycle is delegated to `hash_suite_init` and `hash_suite_exit` from the shared template.

Dependencies: `<crypto/sha2.h>`, generated `sha384-testvecs.h`, KUnit module machinery, and the shared template.

Integration points: registers suite name `sha384`, exercising the public crypto library SHA-384/HMAC functions independent of higher-level protocols.

Risks: this file has little custom logic, so coverage quality depends almost entirely on vector quality and template behavior. It does not add SHA-384-specific edge tests beyond the generated vector set.

Test signals: validates streaming and one-shot hash/HMAC paths through the macro-generated cases, including boundary lengths inherited from the vector header.
