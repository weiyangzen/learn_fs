# sources/distributed-fs/glusterfs/libglusterfs/src/mem-pool.c

## Purpose
`mem-pool.c` provides GlusterFS memory wrappers with optional accounting and guard headers/trailers, `gf_asprintf` helpers, and a per-thread object pool allocator used by `mem_get()`/`mem_put()`. It supports diagnostics for allocation counts, overrun detection, debug object lists, and faster reuse of fixed-size internal objects.

## Important APIs, Types, And Functions
Memory-accounting wrappers are `__gf_malloc()`, `__gf_calloc()`, `__gf_realloc()`, and `__gf_free()`, exposed through `GF_MALLOC`, `GF_CALLOC`, `GF_REALLOC`, and `GF_FREE`. Formatting helpers are `gf_vasprintf()` and `gf_asprintf()`. Memory accounting setup includes `gf_mem_acct_enable_set()`, internal header/trailer helpers, and `gf_mem_set_acct_info()`.

When mem-pools are enabled, lifecycle APIs are `mem_pools_init()`, `mem_pools_fini()`, `mem_pool_new_fn()`, `mem_pool_destroy()`, `mem_get_pool_list()`, `mem_get_malloc()`, `mem_get_calloc()`, `mem_put_pool()`, and `mem_pool_thread_destructor()`. Static process state includes `pools[NPOOLS]`, global live/free thread lists, a thread-local `thread_pool_list`, initialization counters, and a sweeper thread.

## Control Flow
With memory accounting disabled or unavailable early, allocation wrappers call plain `malloc/calloc/realloc/free` through defaults. When enabled, allocation reserves header plus trailer space, stores size/type/accounting pointer/magic in `struct mem_header`, writes a trailer magic byte-by-byte, updates `mem_acct_rec` counters and debug lists, and returns `header->data`. Free subtracts the header size, validates header and trailer magic, decrements accounting counters, destroys memory accounting when the last allocation disappears, optionally poisons the allocation in DEBUG, and frees the full block.

The pool subsystem preinitializes pool size classes in a constructor. `mem_pool_new_fn()` maps a requested object size plus pooled header to a power-of-two class between 128 bytes and 1 MiB and registers the pool on `ctx->mempool_list`. Each thread lazily obtains a `per_thread_pool_list_t`. `mem_get_from_pool()` pops from the per-thread hot list, then cold list, otherwise allocates a class-sized object. `mem_put_pool()` validates the header and pushes the object back to the owning thread's hot list unless that thread pool is poisoned, in which case it frees directly. The sweeper periodically moves hot lists to cold lists and frees previously cold objects outside global locks.

## State And Persistence
All state is in process memory. Accounting records persist for the life of a translator memory-accounting object and are consumed by monitoring/statedump code. Pool shared classes are intentionally permanent after `mem_pool_destroy()`; the pool object is freed, but class storage and outstanding cached objects are reclaimed lazily by the sweeper or thread destructors.

## Dependencies And Integration Points
The file depends on `glusterfs/mem-pool.h`, common utils, globals/`THIS`, logging, pthreads, unit-test hooks, atomic/list primitives, and `gf_thread_create()` / `gf_thread_needs_cleanup()`. Most of GlusterFS uses these wrappers indirectly through macros, so allocator behavior affects nearly every module. `monitoring.c` reads memory accounting records.

## Risks
`req_size = nmemb * size` in `__gf_calloc()` is not explicitly overflow-checked before total-size calculation. Accounting relies on `THIS` and `THIS->ctx`; low-level calls before context setup bypass accounting. `__gf_realloc()` requires non-NULL input and asserts header magic, unlike standard `realloc(NULL, size)`. Header/trailer pointer arithmetic is done on `void *` in GNU C style. Pool objects returned to a thread-local owner can be freed by another thread; the design stores `pool_list` in each object and uses spinlocks plus poison flags, so races in thread teardown are especially sensitive. `mem_pools_postfini()` intentionally leaks at process exit because safe global teardown is unresolved.

## Test Signals
Tests should cover accounted and unaccounted allocation, calloc zeroing, realloc grow/shrink preserving accounting, trailer overrun assertions, double/free-invalid behavior in debug builds, `gf_asprintf()` formatting and ENOMEM paths, pool class selection boundaries, mem_get/mem_put reuse, cross-thread mem_put during thread exit, sweeper hot/cold transitions, `GF_DISABLE_MEMPOOL` builds, and monitoring of `mem_acct_rec` counters.
