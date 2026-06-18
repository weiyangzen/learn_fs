<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-kcapi.c -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy-kcapi.c

Purpose: Adapts the standalone jitterentropy collector to the Linux kernel crypto RNG API as `jitterentropy_rng`, providing allocation, time/hash primitives, initialization tests, and runtime generation.

Important APIs/types/functions: `jent_kvzalloc()`, `jent_kvzfree()`, `jent_zalloc()`, and `jent_zfree()` are memory hooks for the standalone code. `jent_get_nstime()` samples `random_get_entropy()` or `ktime_get_ns()` and feeds the optional test interface. `jent_hash_time()` and `jent_read_random_block()` implement SHA3-256 conditioning. `struct jitterentropy` stores a mutex, collector pointer, and SHA3 state. `jent_kcapi_init()`, `jent_kcapi_cleanup()`, `jent_kcapi_random()`, and `jent_kcapi_reset()` provide the RNG transform operations.

Control flow: Module init enables the test interface, runs `jent_entropy_init()` with configured oversampling, and registers the RNG only if startup health/timer checks pass. Transform init initializes SHA3 and allocates a collector. Generate locks the transform, calls `jent_read_entropy()`, maps collector errors to `-EAGAIN`, `-EFAULT`, or `-EINVAL`, and panics on permanent health-test failure in FIPS mode.

State and persistence behavior: Each RNG transform has independent collector state and SHA3 pool protected by `jent_lock`. Module-level state is limited to crypto registration and optional debugfs test setup. Sensitive SHA3 and collector memory are zeroed/freed on cleanup.

Dependencies and integration points: Integrates with `crypto/internal/rng.h`, SHA3 primitives, Linux timing sources, FIPS policy, KMSAN unpoisoning, and `jitterentropy-testing.c` through `jent_raw_hires_entropy_store()`.

Risks: Entropy quality depends on high-resolution timer behavior and compiler constraints from `jitterentropy.c`. Permanent health failures in FIPS mode intentionally panic the kernel. Locking serializes generation per transform; misuse without the mutex would corrupt collector state. `seed()` is a no-op, so callers cannot reseed this RNG externally.

Test signals: Module load on supported/unsupported timers, RNG generation through the crypto API, FIPS and non-FIPS permanent/intermittent health failure behavior, debugfs raw timer capture when enabled, KMSAN clean output buffers, and repeated init/exit leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-kcapi.c -->
