# sources/distributed-fs/ceph-client/lib/crypto/tests/sha256_kunit.c

Purpose: KUnit coverage and optional benchmarking for SHA-256, HMAC-SHA256, and the optimized two-message finalization helper `sha256_finup_2x()`.

Important APIs/types/functions: it binds `HASH`, `HASH_CTX`, `HASH_INIT`, `HASH_UPDATE`, `HASH_FINAL`, and the HMAC macro family to the shared `hash-test-template.h`. Local helpers include `alloc_guarded_buf()`, `test_sha256_finup_2x()`, `test_sha256_finup_2x_defaultctx()`, `test_sha256_finup_2x_hugelen()`, and `benchmark_sha256_finup_2x()`.

Control flow: the template contributes `HASH_KUNIT_CASES` and `benchmark_hash`. The custom finup test allocates vmalloc-backed buffers ending at a page boundary, fills random data and salt, prepares an initial context, calls `sha256_finup_2x()`, asserts the input context is unchanged, and compares both outputs with ordinary `sha256_update()`/`sha256_final()` results. The default-context test compares a NULL context against an initialized empty context. The huge-length test seeds the internal bytecount above 32 bits and verifies finalization length encoding. Benchmark cases skip unless `CONFIG_CRYPTO_LIB_BENCHMARK` and optimized finup support are present.

State and persistence: all buffers are KUnit-managed through `kunit_add_action_or_reset()` and freed with `vfree`; no persistent state. It mutates temporary hash contexts and a shared test buffer from the template.

Dependencies: `<crypto/sha2.h>`, generated SHA-256 vectors, KUnit, vmalloc, random test helpers from the template, timing helpers, and optional crypto benchmark config.

Integration points: registers suite `sha256`; validates architecture and generic SHA-256 paths exposed behind the public SHA-2 library API.

Risks: guarded-buffer arithmetic returns `buf + full_len - len`; zero-length allocations rely on caller behavior and current test lengths. Randomized loops increase coverage but failures need logged salt/data lengths to reproduce. Optimized assembly errors are specifically targeted through guard pages.

Test signals: strong correctness signal for SHA-256, HMAC, context immutability, tail padding, huge byte counts, and out-of-bounds accesses in optimized finup paths.
