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
