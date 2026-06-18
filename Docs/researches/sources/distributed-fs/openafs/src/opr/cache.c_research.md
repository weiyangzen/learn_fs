# sources/distributed-fs/openafs/src/opr/cache.c

Purpose: simple thread-safe in-memory cache for flat binary keys and values.

Important APIs/types/functions: public `opr_cache_init`, `opr_cache_free`, `opr_cache_get`, and `opr_cache_put`; structures `opr_cache` and `cache_entry`. Internal functions include `free_entry_contents`, `evict_entry`, `alloc_entry`, `find_entry`, `memdup`, `isPowerOf2`, and `nextPowerOf2`.

Control flow: initialization validates bucket/entry bounds, rounds bucket count up to a power of two, initializes a mutex, and creates an `opr_dict`. `put` duplicates key/value, locks, finds or allocates an entry, and replaces the value. If full, allocation evicts a random bucket's least-recently-used entry. `get` locks, finds and promotes the entry in its bucket, checks output buffer capacity, and copies bytes. Free scans every bucket and frees entries.

State and persistence: cache state is heap memory protected by `opr_mutex_t`; entries are held in dictionary buckets using intrusive queues. No persistence.

Dependencies/integration: uses `opr/dict.h`, `opr/queue.h`, Jenkins hash from `opr/jhash.h`, and either pthread locks or `lockstub.h` for LWP/non-pthread builds.

Risks and test signals: `rand()` is used without seeding/control. `get` assumes `a_val_len` is valid and `val_buf` has the specified size. Null cache acts as empty. Tests should cover invalid options, duplicate puts, ENOSPC gets, eviction, and threaded access.
