# sources/distributed-fs/ceph-client/crypto/algapi.c

Purpose: implements the low-level crypto algorithm registry and template/spawn infrastructure. It validates algorithms, manages registration/unregistration, self-test larvals, template instances, dependency removal, notifier registration, async request queues, counter increment helpers, and boot-time self-test startup.

Important APIs, types, and functions: exported APIs include `crypto_register_alg()`, `crypto_unregister_alg()`, batch helpers, `crypto_register_template()`, `crypto_unregister_template()`, `crypto_lookup_template()`, `crypto_register_instance()`, `crypto_unregister_instance()`, `crypto_grab_spawn()`, `crypto_drop_spawn()`, `crypto_spawn_tfm()`, `crypto_spawn_tfm2()`, notifier helpers, attr parsing helpers, `__crypto_inst_setname()`, queue helpers, `crypto_inc()`, `crypto_alg_extsize()`, `crypto_type_has_alg()`, and `crypto_alg_tested()`.

Control flow and behavior: registration validates module signatures in FIPS mode, names, alignment, blocksize, priority, and duplicate names. With self-tests enabled, an untested algorithm is registered alongside a larval placeholder; `cryptomgr` later reports results through `crypto_alg_tested()`, which marks success/failure and notifies waiters. Templates register separately, create instances with spawns, and dependency trees are walked depth-first when underlying algorithms are removed or superseded.

State and persistence: global crypto algorithm/template lists are protected by `crypto_alg_sem`. Algorithms track refcounts, flags, user spawn lists, larval completions, and module refs. Templates maintain live and dead instance lists plus deferred free work. Async queues store request lists, backlog pointer, length, and max length.

Dependencies and integration points: depends on `internal.h` globals, crypto notifier chain, module refs/signatures, workqueues, rtnetlink-era list locking conventions, `cryptomgr` self-test scheduling, and all crypto front ends/templates that register algorithms or spawn children.

Risks and correctness concerns: registry locking and refcounts are critical; mistakes can produce UAFs during module unload or template removal. Spawn dependency pruning must avoid deleting instances needed by a newly registered replacement. FIPS signature checks panic on invalid modules. Larval/test state must never expose untested algorithms as tested. Queue backlog semantics affect async engine fairness.

Test signals: concurrent register/unregister stress, module unload with dependent templates, self-test pass/fail/`-ECANCELED` paths, FIPS module signature failure behavior, duplicate names/priorities, template instance creation/removal, spawn refcount leaks, async queue full/backlog behavior, and `crypto_inc()` counter vectors.
