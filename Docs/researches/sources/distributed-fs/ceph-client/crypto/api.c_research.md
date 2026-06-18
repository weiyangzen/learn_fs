# sources/distributed-fs/ceph-client/crypto/api.c

Purpose: provides the core Linux Crypto API transform allocation, algorithm lookup, module autoload, larval placeholder, selftest, notifier, and transform destruction machinery. It is the central registry-facing runtime for crypto algorithm consumers and providers.

Important APIs/types/functions: global exported objects include `crypto_alg_list`, `crypto_alg_sem`, and `crypto_chain`. `crypto_mod_get()` and `crypto_mod_put()` manage algorithm and module references. `crypto_larval_alloc()`, `crypto_larval_add()`, `crypto_larval_wait()`, and `crypto_larval_kill()` represent algorithms being probed, tested, or instantiated by cryptomgr. `crypto_alg_mod_lookup()`, `crypto_find_alg()`, `crypto_alloc_base()`, and `crypto_alloc_tfm_node()` locate and allocate transforms. `crypto_create_tfm_node()`, `crypto_clone_tfm()`, and `crypto_destroy_tfm()` manage transform memory and lifecycle hooks. `crypto_req_done()` is the common completion helper.

Control flow: lookup first scans registered algorithms under `crypto_alg_sem`, prefers exact driver-name matches or highest-priority generic-name matches, and filters type/mask/FIPS/internal/tested flags. If no usable algorithm exists, it can `request_module("crypto-%s")`, ask cryptomgr through `crypto_chain`, insert a larval, wait up to 60 seconds, and retry on `-EAGAIN` unless interrupted. Allocation wraps lookup, algorithm reference acquisition, frontend type initialization, optional provider `cra_init`, and rollback on failure. Destruction runs frontend/provider exit hooks and drops algorithm/module references.

State and persistence: algorithm registration state is process-global kernel memory protected by `crypto_alg_sem`. Larvals carry completions, probe state, and adult algorithm pointers until killed. Transforms store their algorithm pointer, refcount, NUMA node, frontend backing, and provider context until freed. No filesystem persistence exists.

Dependencies and integration points: depends on `internal.h`, module loading, completions, blocking notifier chains, static keys for boot selftests, crypto type frontends, and cryptomgr. Nearly every higher-level crypto allocation path ultimately depends on this file.

Risks: lookup and larval state are concurrency-sensitive; missed completions, refcount mistakes, or lock-order issues can hang callers or unload live modules. FIPS/internal/tested mask rules are subtle and easy to bypass accidentally. `crypto_request_clone()` falls back to the original request when allocation fails, so callers must understand ownership. Timeout and signal handling must not leave dead larvals in the registry.

Test signals: module autoload success/failure, cryptomgr fallback, larval timeout, interrupted allocation, tested/FIPS-internal filtering, provider `cra_init` returning `-EAGAIN`, NUMA allocation paths, clone fallback, and repeated concurrent allocation of the same algorithm are important signals.
