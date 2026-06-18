# sources/distributed-fs/ceph-client/lib/crypto/tests/hash-test-template.h

## Purpose
This header is a reusable KUnit test and benchmark template for kernel hash-like APIs. Including suites define macros for one-shot hash, context type, digest size, init/update/final functions, and optionally HMAC functions. The template then emits common test functions, suite init/exit helpers, case macros, deterministic test data generation, guard-page safety checks, interrupt-context checks, and a gated benchmark.

## Important APIs, Types, and Functions
- Required macros: `HASH`, `HASH_CTX`, `HASH_SIZE`, `HASH_INIT`, `HASH_UPDATE`, and `HASH_FINAL`.
- Optional HMAC macros: `HMAC_KEY`, `HMAC_CTX`, `HMAC_PREPAREKEY`, `HMAC_INIT`, `HMAC_UPDATE`, `HMAC_FINAL`, `HMAC`, and `HMAC_USINGRAWKEY`.
- `TEST_BUF_LEN` is 16384, and `test_buf` is positioned so `&test_buf[TEST_BUF_LEN]` is unmapped when `vmalloc()` provides a guard page after a page-aligned allocation.
- The deterministic PRNG is `rand32()` with a hard-coded linear congruential generator, plus helpers `rand_bytes()`, `rand_bytes_seeded_from_len()`, `rand_bool()`, `rand_length()`, and `rand_offset()`.
- `hash_suite_init()` allocates the guarded buffer; `hash_suite_exit()` frees it.
- Generic tests include `test_hash_test_vectors`, `test_hash_all_lens_up_to_4096`, `test_hash_incremental_updates`, `test_hash_buffer_overruns`, `test_hash_overlaps`, `test_hash_alignment_consistency`, `test_hash_ctx_zeroization`, `test_hash_interrupt_context_1`, and `test_hash_interrupt_context_2`.
- `test_hmac()` is emitted only when `HMAC` is defined and checks raw/prepared key consistency, consolidated HMAC output, and HMAC context zeroization.
- `UNKEYED_HASH_KUNIT_CASES` and `HASH_KUNIT_CASES` expose the generated cases to including suites.
- `benchmark_hash()` measures throughput for selected lengths when `CONFIG_CRYPTO_LIB_BENCHMARK` is enabled.

## Control Flow
Including suites define algorithm-specific macros and include this header. The suite calls `hash_suite_init()` before cases and `hash_suite_exit()` afterward. Vector tests generate seeded data based on vector length, run one-shot hash, and compare against `hash_testvecs[]`. Exhaustive-length testing hashes every length from 0 to 4096 and then hashes the digest stream. Incremental tests split random inputs into random update sequences and compare to one-shot output. Guard tests place data, digest output, or context at the end of the guarded allocation. Overlap tests intentionally alias output with the input region and mutate input after update. IRQ tests use `kunit_run_irq_test()` to run hash operations and incremental state transitions concurrently across task/softirq/hardirq contexts. Benchmarking warms up and then times selected lengths under `preempt_disable()`.

## State and Persistence Behavior
The template owns static globals `test_buf`, `orig_test_buf`, and `random_seed` in each translation unit that includes it. The buffer is allocated at suite init and freed at suite exit. The PRNG state is deterministic but mutable throughout tests; it is reset by length-seeded helper calls for vector-style tests. No persistent state crosses module unload/reload.

## Dependencies and Integration Points
The template depends on KUnit assertions, `kunit_run_irq_test()`, `vmalloc()`/`vfree()`, page-size/rounding helpers, atomics, preemption/timing helpers available through included kernel headers, and algorithm-specific vector symbols `hash_testvecs`, `hash_testvec_consolidated`, and optionally `hmac_testvec_consolidated`. It is consumed by MD5, SHA-1, SHA-224, GHASH, POLYVAL, and Poly1305 suites in this subset.

## Risks and Edge Cases
The header emits static symbols, so it must be included in only one suite translation unit per macro configuration. Template users must ensure `HASH_FINAL` zeroizes the context if they opt into the generic zeroization test. The guard-page assumption relies on the vmalloc allocation layout described in the comments. The deterministic PRNG is intentionally non-cryptographic; changing it breaks generated test-vector compatibility. The IRQ tests assume `IRQ_TEST_NUM_BUFFERS` matches `kunit_run_irq_test()` max concurrency. `test_hmac()` uses one consolidated oracle, which gives broad coverage but does not identify the exact failing data/key length.

## Test Signals
This template supplies broad behavior signals: known-answer correctness, exhaustive small-length coverage, incremental equivalence, data/output/context overrun checks, output-input aliasing, post-update input independence, alignment consistency, context zeroization, interrupt-context safety, HMAC wrapper correctness, and optional throughput measurements.
