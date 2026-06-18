# sources/distributed-fs/ceph-client/lib/crypto/tests/sha512_kunit.c

Purpose: minimal KUnit suite wiring for SHA-512 and HMAC-SHA512 using generated vectors and the shared hash test template.

Important APIs/types/functions: maps `HASH_*` macros to `sha512_ctx`, `sha512_init()`, `sha512_update()`, `sha512_final()`, and maps HMAC macros to `hmac_sha512_*` APIs. Registers `hash_test_cases[]` with `HASH_KUNIT_CASES` and `benchmark_hash`.

Control flow: template-generated tests execute the vector table and consolidated HMAC checks. The benchmark case is included in the suite and is controlled by the template/config runtime skip behavior.

State and persistence: no local allocations or persistent state; suite init/exit are delegated to the shared hash test template.

Dependencies: `<crypto/sha2.h>`, `sha512-testvecs.h`, KUnit, and `hash-test-template.h`.

Integration points: suite name `sha512`; validates the crypto library SHA-512 public API and HMAC API used by kernel consumers.

Risks: no SHA-512-specific custom edge tests beyond generated vectors. Any flaw in `hash-test-template.h` affects this suite and other hash suites in the same pattern.

Test signals: verifies update/final sequencing, one-shot/HMAC helper consistency, and performance benchmark availability for SHA-512.
