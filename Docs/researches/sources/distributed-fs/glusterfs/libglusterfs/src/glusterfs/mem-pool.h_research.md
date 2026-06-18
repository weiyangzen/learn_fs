# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-pool.h

Purpose: `mem-pool.h` defines GlusterFS allocation wrappers, memory-accounting headers, debug sentinels, string/memory duplication helpers, and the optional per-thread fixed-size object pool API.

Important APIs and types: `struct mem_acct` and `struct mem_acct_rec` track allocation counts and, under `DEBUG`, sizes and object lists. `struct mem_header` stores accounting pointer, allocation size, type, and magic. Public allocators are `__gf_malloc`, `__gf_calloc`, `__gf_realloc`, `__gf_free`, `GF_MALLOC`, `GF_CALLOC`, `GF_REALLOC`, and `GF_FREE`. Pool APIs include `mem_pool_new_fn`, `mem_get_malloc`, `mem_get_calloc`, `mem_put_pool`, `mem_pool_destroy`, `mem_pools_init`, and `mem_pools_fini`.

Control flow and state: default allocation wrappers log no-memory alerts. With mempool enabled, `struct mem_pool` links to `glusterfs_ctx_t->mempool_list`, tracks active allocations, and uses per-thread hot/cold lists guarded by spinlocks. With `GF_DISABLE_MEMPOOL`, `mem_pool` becomes a size wrapper and `mem_get`/`mem_put` fall back to normal GF allocation.

Dependencies and integration: nearly every file in this subset uses these macros for source-type accounting. `stack.h` allocates call frames/stacks from pools; graph and parser code allocate translators and lists with common memory types.

Risks: use-after-free detection depends on magic/header discipline. `FREE` poisons raw pointers but `GF_FREE` ownership is implementation-defined. Pool object headers reduce available size and require correct size-class selection. Thread-local pool destruction and sweeper behavior are concurrency-sensitive.

Test signals: allocation accounting tests, debug magic corruption tests, mempool enabled/disabled builds, thread exit destructor behavior, and leak/statedump validation are high-value. Fuzzing should include zero-size and realloc failure cases.
