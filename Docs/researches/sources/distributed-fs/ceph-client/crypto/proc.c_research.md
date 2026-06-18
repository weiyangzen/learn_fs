# sources/distributed-fs/ceph-client/crypto/proc.c

Purpose: implements `/proc/crypto`, a procfs sequence view of registered crypto algorithms.

Important APIs and functions: `crypto_init_proc()` creates the `crypto` proc entry, and `crypto_exit_proc()` removes it. Sequence callbacks `c_start()`, `c_next()`, `c_stop()`, and `c_show()` iterate `crypto_alg_list` under `crypto_alg_sem`.

Control flow: opening `/proc/crypto` starts a seq iteration while holding the crypto algorithm read semaphore. For each `struct crypto_alg`, `c_show()` prints name, driver, module, priority, refcount, selftest state, internal flag, optional FIPS status, and type-specific details. Larval algorithms are reported separately. Algorithms with a `cra_type->show` hook delegate formatting to that type; legacy cipher algorithms are formatted inline.

State and persistence: the file owns no algorithm state. It reads the live in-memory registry and emits a transient procfs view.

Dependencies and integration points: depends on `crypto_alg_list`, `crypto_alg_sem`, `module_name()`, FIPS state, procfs, and type-specific `.show` callbacks such as hash, rng, skcipher, lskcipher, or scomp reporting.

Risks: output is diagnostic ABI-like text; changes can affect userspace tools that parse `/proc/crypto`. The read lock must cover list traversal. Type-specific show hooks must not sleep in ways incompatible with the read-side locking expectations.

Test signals: procfs read under concurrent algorithm registration/unregistration, FIPS-enabled output, larval entries, type-specific formatting, and absence of use-after-free under module unload stress.
