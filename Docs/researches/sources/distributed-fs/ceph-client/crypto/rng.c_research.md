# sources/distributed-fs/ceph-client/crypto/rng.c

Purpose: implements the crypto API RNG type, default RNG management, seeding helper, reporting, allocation, and registration functions.

Important APIs and functions: exported functions include `crypto_rng_reset()`, `crypto_alloc_rng()`, `__crypto_stdrng_get_bytes()`, `crypto_del_default_rng()`, `crypto_register_rng()`, `crypto_unregister_rng()`, `crypto_register_rngs()`, and `crypto_unregister_rngs()`. Global state is `crypto_default_rng`, `crypto_default_rng_refcnt`, and `crypto_default_rng_lock`.

Control flow: `crypto_rng_reset()` seeds a tfm directly, or if `seed == NULL` with nonzero length, allocates a temporary seed and fills it with `get_random_bytes_wait()`. Default RNG access lazily allocates `stdrng`, seeds it with its required seed size, increments a protected refcount, gets bytes, then decrements the refcount. Registration installs the RNG crypto type, enforces seed size no larger than `PAGE_SIZE / 8`, and fills a no-op `set_ent` callback when absent.

State and persistence: the default RNG tfm is a global in-memory singleton protected by a mutex and refcount. Temporary seeds are wiped with `kfree_sensitive()`. Algorithm registrations persist while providers are loaded.

Dependencies and integration points: depends on the generic crypto type registry, `get_random_bytes_wait()`, procfs/netlink reporting hooks, and providers such as `stdrng`.

Risks: `crypto_put_default_rng()` decrements without underflow checking beyond mutex serialization; callers must pair get/put internally. Default RNG deletion returns `-EBUSY` while refs are active. Blocking entropy acquisition can affect init timing. Seed-size validation is part of memory safety.

Test signals: default RNG lazy allocation, deletion while busy and idle, seed reset with caller seed and generated seed, proc/netlink reporting, seed-size rejection, and registration rollback for arrays.
