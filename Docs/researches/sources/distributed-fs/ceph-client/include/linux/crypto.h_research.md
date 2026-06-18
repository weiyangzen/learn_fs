<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crypto.h -->
# sources/distributed-fs/ceph-client/include/linux/crypto.h

## Purpose

`crypto.h` defines the generic Linux kernel crypto transform and algorithm registration contract. It covers algorithm type/flag masks, transform request flags, algorithm descriptors, async request completion, transform allocation/destruction, and small inline query/request helpers. The source was read as a complete 529-line file.

## Important APIs, Types, and Functions

Constants include `CRYPTO_ALG_TYPE_*`, algorithm state/feature flags such as `CRYPTO_ALG_ASYNC`, `CRYPTO_ALG_NEED_FALLBACK`, `CRYPTO_ALG_INTERNAL`, `CRYPTO_ALG_ALLOCATES_MEMORY`, `CRYPTO_ALG_FIPS_INTERNAL`, `CRYPTO_ALG_REQ_VIRT`, and transform request flags like `CRYPTO_TFM_REQ_MAY_SLEEP`, `MAY_BACKLOG`, and `ON_STACK`. Types include `crypto_completion_t`, `struct crypto_async_request`, `struct cipher_alg`, `struct crypto_alg`, `struct crypto_wait`, and `struct crypto_tfm`. APIs include `crypto_req_done()`, `crypto_wait_req()`, `crypto_init_wait()`, `crypto_has_alg()`, `crypto_alloc_base()`, `crypto_destroy_tfm()`, `crypto_free_tfm()`, transform query helpers, flag setters/clearers, `crypto_tfm_is_async()`, `crypto_req_on_stack()`, `crypto_request_set_callback()`, `crypto_request_set_tfm()`, `crypto_request_clone()`, and `crypto_stack_request_init()`.

## Control Flow

Algorithm providers register `struct crypto_alg` instances with names, flags, priority, context sizes, callbacks, and module owner. Users allocate transforms by algorithm name/type/mask, configure request callbacks, submit operations through type-specific APIs, and handle async completion. `crypto_wait_req()` converts `-EINPROGRESS` or `-EBUSY` into a blocking wait on `struct crypto_wait`.

## State and Persistence Behavior

`struct crypto_alg` persists while registered and is refcounted by users. `struct crypto_tfm` is a user-instantiated transform with flags, NUMA node, optional fallback transform, algorithm pointer, and aligned private context. `struct crypto_async_request` carries per-operation state and callbacks. No disk persistence is involved.

## Dependencies and Integration Points

It depends on completions, errno, refcount types, slab allocation, and common types. It integrates with type-specific crypto APIs such as skcipher, aead, hash, rng, akcipher, kpp, compression, template instances, module loading, self-tests, and hardware accelerators.

## Risks and Edge Cases

Alignment and allocation flags are security/performance-sensitive. Algorithms marked not allocating memory still have documented edge cases unless users satisfy alignment and scatterlist constraints. Async callbacks must handle backlog and completion races. Stack requests must preserve `CRYPTO_TFM_REQ_ON_STACK`. Algorithm flags determine fallback, FIPS/internal visibility, userspace exposure, and module loading behavior.

## Test Signals

Signals include crypto selftests, algorithm registration/unregistration, transform allocation by name/type/mask, async completion and `crypto_wait_req()` behavior, fallback tests, alignment stress, no-allocation request tests, FIPS/internal visibility checks, and hardware/software equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crypto.h -->
