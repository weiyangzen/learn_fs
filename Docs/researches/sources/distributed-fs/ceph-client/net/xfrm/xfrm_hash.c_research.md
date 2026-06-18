# sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.c

Purpose: `xfrm_hash.c` provides common allocation and free helpers for XFRM hash tables used by policy and state databases.

Important APIs: `xfrm_hash_alloc(unsigned int sz)` returns a zeroed `struct hlist_head` array using `kzalloc()` for page-sized or smaller allocations, `vzalloc()` for distributed large allocations when `hashdist` is set, or contiguous pages via `__get_free_pages()` otherwise. `xfrm_hash_free()` mirrors the allocation path with `kfree()`, `vfree()`, or `free_pages()`.

Control flow and dependencies: Callers pass byte size, not element count. The helper chooses allocation strategy based on `PAGE_SIZE` and the global `hashdist` memory-allocation policy. It includes `xfrm_hash.h` for declarations and Linux memory APIs for allocation.

State and persistence: No state is retained by this file. Hash table contents are owned by callers; this helper only allocates zeroed bucket arrays and releases them.

Integration points: Used by XFRM policy/state hash infrastructure when resizing or initializing hash buckets. Correct zero initialization matters because empty hlist heads must begin as null.

Risks: Caller size mismatches or freeing with a different size than allocation can call the wrong free path. Large contiguous allocation without `hashdist` can fail under fragmentation; `vzalloc()` avoids that at the cost of vmalloc overhead. No overflow checking is performed here, so callers must compute `sz` safely.

Test signals: Exercise policy/state hash initialization and resize with small and large table sizes, with `hashdist` enabled and disabled. Use memory-pressure tests and KASAN/KMSAN to catch mismatched size/free paths.
