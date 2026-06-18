<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-testing.c -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy-testing.c

Purpose: Provides an optional debugfs interface for collecting raw high-resolution timing samples from jitterentropy for SP800-90B style analysis and boot-time data capture.

Important APIs/types/functions: `struct jent_testing` stores a 1024-entry u64 ring buffer, reader/writer indices, enable flag, spinlock, and waitqueue. `jent_testing_store()` records samples and handles boot-test state transitions. `jent_testing_reader()` drains samples into an aligned kernel buffer, optionally blocking for runtime samples. `jent_testing_extract_user()` copies chunks to userspace. `jent_raw_hires_entropy_store()` is the exported producer hook, and `jent_testing_init()/exit()` create/remove `debugfs/<module>/jent_raw_hires`.

Control flow: On init, debugfs is created. Every `jent_get_nstime()` call may call the store hook. Reads from `jent_raw_hires` enable runtime collection unless boot capture is active, drain u64 samples in chunks, block on the waitqueue if no data is available, and disable/reset runtime capture when done.

State and persistence behavior: State is module-global in `jent_raw_hires` and `boot_raw_hires_test`. Boot mode keeps the collected buffer available until read; runtime mode resets the buffer on entry/exit. No data persists beyond module lifetime or debugfs removal.

Dependencies and integration points: Depends on debugfs, module parameters, wait queues, spinlocks, atomics, user copy helpers, and the jitterentropy header. The production code calls it through inline no-ops when `CONFIG_CRYPTO_JITTERENTROPY_TESTINTERFACE` is disabled.

Risks: This intentionally exposes raw timing data through debugfs and should remain optional and root-readable. Ring buffer wrap and boot-state transitions must avoid losing the first boot samples unexpectedly. Reader blocking must handle signals and scheduling. `debugfs_create_file_unsafe()` is acceptable only because lifetime is controlled by module teardown.

Test signals: Enable the config, read `jent_raw_hires`, verify u64-aligned sample counts, exercise `boot_raw_hires_test=1`, interrupt a blocking read, test multiple partial reads for at least 1000 samples, and ensure debugfs cleanup removes all files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-testing.c -->
