<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/internal.h -->
# sources/distributed-fs/ceph-client/crypto/internal.h

Purpose: Declares core internal crypto API structures and helpers shared by algorithm lookup, larval/test handling, template/type frontends, transform allocation, proc reporting, notifications, and reference management.

Important APIs/types/functions: `struct crypto_larval` represents a placeholder algorithm awaiting testing or module resolution. `struct crypto_type` defines frontend-specific callbacks and sizing. The header declares algorithm lookup/allocation (`crypto_find_alg()`, `crypto_alg_mod_lookup()`, `crypto_alloc_tfm_node()`), larval testing (`crypto_larval_alloc()`, `crypto_schedule_test()`, `crypto_alg_tested()`), spawn removal, transform creation/clone helpers, notifier helpers, module/template ref helpers, and predicates for larval/dead/moribund algorithms.

Control flow: Runtime crypto allocation uses frontend `crypto_type` metadata to find an algorithm, load modules if needed, create a transform on a NUMA node, and run algorithm tests through larvals before making an adult algorithm visible. Registration/removal paths use the declared global algorithm list, semaphore, notifier chain, and spawn cleanup helpers.

State and persistence behavior: Declares global registry state: `crypto_alg_sem`, `crypto_alg_list`, `crypto_chain`, and optionally the static key marking boot self-test completion. Algorithm and transform lifetimes are reference-counted through `crypto_alg_get/put()`, template module refs, and `crypto_tfm_get()`.

Dependencies and integration points: Pulls in algapi, notifier, completion, module, NUMA, refcount, scatterlist, and scheduler primitives. It is consumed by many crypto core frontends, including hash, kpp, skcipher, aead, and template implementations.

Risks: This is central registry infrastructure. Reference-counting mistakes can leak modules or free algorithms while still visible. Larval/test state races can expose untested algorithms or block lookups. Static-key behavior differs when algapi is modular or selftests are disabled, so boot-test assumptions must match config.

Test signals: Crypto manager selftests, module autoload lookup, concurrent algorithm registration/removal, `/proc/crypto` reporting when enabled, notifier events, transform clone/allocation tests, and KASAN/KCSAN coverage of algorithm lifetime and larval completion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/internal.h -->
