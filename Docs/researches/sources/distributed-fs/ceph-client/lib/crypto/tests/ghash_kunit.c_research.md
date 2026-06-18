# sources/distributed-fs/ceph-client/lib/crypto/tests/ghash_kunit.c

## Purpose
This file adapts the keyed GHASH API to the shared hash test template, then adds GHASH-specific checks for prepared-key safety, alignment, all-one-bits arithmetic stress, interrupt-context key preparation, and optional throughput benchmarking.

## Important APIs, Types, and Functions
- `static struct ghash_key test_key` is the fixed suite key used to present GHASH as an unkeyed hash to `hash-test-template.h`.
- `ghash_init_withtestkey()` and `ghash_withtestkey()` wrap `ghash_init()` and `ghash()` using `test_key`.
- The template macros bind `HASH`, `HASH_CTX`, `HASH_SIZE`, `HASH_INIT`, `HASH_UPDATE`, and `HASH_FINAL` to GHASH wrappers and context types.
- `test_ghash_allones_key_and_message()` prepares an all-ones key, hashes all-ones messages from 0 to 4096 bytes in 16-byte steps, hashes those hashes, and compares to `ghash_allones_hashofhashes`.
- `check_key_consistency()` verifies two prepared keys are byte-identical and produce matching hashes over random lengths up to `MAX_LEN_FOR_KEY_CHECK`.
- `test_ghash_with_guarded_key()` checks `ghash_preparekey()` does not overread raw keys or prepared-key output when either ends at the guard page.
- `test_ghash_with_minimally_aligned_key()` verifies `struct ghash_key` only requires its declared alignment, not a stronger vector alignment.
- `test_ghash_preparekey_in_irqs()` uses `kunit_run_irq_test()` to confirm `ghash_preparekey()` gives the same prepared key when called from task, softirq, and hardirq-like contexts.
- `ghash_suite_init()` seeds and prepares `test_key`, then delegates shared guarded-buffer setup to `hash_suite_init()`.

## Control Flow
Suite initialization prepares the fixed test key from deterministic random bytes and allocates the shared guarded test buffer. Template-generated cases then run known-answer, all-length, incremental, guard-page, overlap, alignment, zeroization, IRQ, and benchmark tests. GHASH-specific cases run after the template cases and before benchmark. Suite exit frees the guarded buffer through `hash_suite_exit()`.

## State and Persistence Behavior
The only suite state is `test_key` plus the shared `test_buf`, `orig_test_buf`, and deterministic `random_seed` from `hash-test-template.h`. State is initialized once per suite and released at suite exit. No persistent filesystem or cross-module state exists.

## Dependencies and Integration Points
The file depends on `<crypto/gf128hash.h>`, `ghash-testvecs.h`, `hash-test-template.h`, KUnit, `vmalloc()` guard-page behavior from the template, and `kunit_run_irq_test()` from the template include path. It registers KUnit suite name `ghash`.

## Risks and Edge Cases
The test intentionally relies on bytewise equality of prepared keys; architecture-specific implementations must produce canonical prepared-key layouts, not just equivalent behavior. Guarded-buffer tests catch overreads only at the end boundary used by the template. The IRQ test is a strong signal for FPU/vector-state handling, but it only checks preparation output equality, not full GHASH execution in every context.

## Test Signals
Signals include generic hash API behavior from the shared template, GHASH vector oracles, all-one-bits overflow stress, guard-page key overread detection, minimal-alignment verification, interrupt-context key preparation, and optional benchmark throughput.
