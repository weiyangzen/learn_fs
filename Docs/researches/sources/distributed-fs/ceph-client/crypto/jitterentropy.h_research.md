<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.h -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy.h

Purpose: Declares the interface between the standalone jitterentropy core, the kernel crypto API adapter, and the optional test interface.

Important APIs/types/functions: Declares allocation hooks, `jent_get_nstime()`, SHA3 conditioning hooks `jent_hash_time()` and `jent_read_random_block()`, opaque `struct rand_data`, collector lifecycle `jent_entropy_collector_alloc/free()`, initialization `jent_entropy_init()`, and generation `jent_read_entropy()`. It also exposes `jent_raw_hires_entropy_store()`, `jent_testing_init()`, and `jent_testing_exit()` or inline no-ops depending on `CONFIG_CRYPTO_JITTERENTROPY_TESTINTERFACE`.

Control flow: No executable flow exists in the header except test-interface no-op inlines. Including files use it to call from the collector into kernel-provided hooks and from the kernel adapter into the collector.

State and persistence behavior: The header stores no state. It defines the opaque collector boundary so `struct rand_data` state remains private to `jitterentropy.c`.

Dependencies and integration points: Depends on `struct sha3_ctx` and kernel fixed-width integer types. Bridges `jitterentropy.c`, `jitterentropy-kcapi.c`, and `jitterentropy-testing.c`.

Risks: Prototype mismatches would break the delicate separation between standalone and kernel-specific code. Inline no-ops must exactly match optional test behavior so production builds do not depend on debugfs symbols.

Test signals: Build both with and without `CONFIG_CRYPTO_JITTERENTROPY_TESTINTERFACE`, verify no unresolved symbols, and run jitterentropy module init/generation in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.h -->
