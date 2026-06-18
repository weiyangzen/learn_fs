# sources/distributed-fs/ceph-client/crypto/algboss.c

Purpose: implements the crypto manager notifier that instantiates template algorithms on demand and schedules algorithm self-tests in kernel threads.

Important APIs, types, and functions: key structures are `cryptomgr_param` for template instantiation and `crypto_test_param` for self-tests. Main functions are `cryptomgr_probe()`, `cryptomgr_schedule_probe()`, `cryptomgr_test()`, `cryptomgr_schedule_test()`, `cryptomgr_notify()`, and module init/exit registering `cryptomgr_notifier`.

Control flow and behavior: on `CRYPTO_MSG_ALG_REQUEST`, it parses names like `cbc(aes)` into a template name and nested algorithm attributes, builds rtattr arrays, and starts `cryptomgr_probe` to call the template’s `create()` method until success or signal. On `CRYPTO_MSG_ALG_REGISTER`, it starts `cryptomgr_test`, which runs `alg_test()` and reports back through `crypto_alg_tested()`. `CRYPTO_MSG_ALG_LOADED` is ignored.

State and persistence: all operation-specific state is heap-allocated and owned by the spawned kthread. Larval completions bridge async instantiation back to waiters. The module persists only a notifier block.

Dependencies and integration points: depends on crypto notifier chain, template lookup, larval algorithms from `algapi.c`, `testmgr` via `alg_test()`, kthreads, module refcounts, and rtattr-compatible template parameters.

Risks and correctness concerns: parser correctness is important for nested template names; malformed names must not overrun fixed arrays or leak module refs. Kthread creation failures must release larval/module references. Probe loops on `-EAGAIN` must stop on pending signals. Self-tests are optional by Kconfig but are central for FIPS/production confidence.

Test signals: request algorithms such as `cbc(aes)`, nested templates, malformed names, missing templates, kthread failure injection, self-test pass/fail notifications, module unload while work is active, and boot-time self-test scheduling from `algapi.c`.
