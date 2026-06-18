# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-resv.c

Purpose: implements reservation objects, the dma-buf synchronization container that stores fences tagged by usage and protected by a ww_mutex plus RCU for lockless readers.

Important APIs/types/functions: exports `reservation_ww_class`, `dma_resv_init()`, `dma_resv_fini()`, `dma_resv_reserve_fences()`, `dma_resv_add_fence()`, `dma_resv_replace_fences()`, locked/unlocked iterators, `dma_resv_copy_fences()`, `dma_resv_get_fences()`, `dma_resv_get_singleton()`, `dma_resv_wait_timeout()`, `dma_resv_set_deadline()`, `dma_resv_test_signaled()`, and `dma_resv_describe()`. Internal `struct dma_resv_list` packs fence pointer plus usage bits in the low pointer bits.

Control flow: init creates the ww_mutex and clears the RCU fence-list pointer. Reserving fences allocates or grows the list, compacts out already signaled fences, publishes the new list via RCU, and drops references to signaled fences. Adding a fence requires the lock and prior reservation, takes a reference, replaces older/signed fences where possible, or appends a new entry with a write barrier before raising `num_fences`. Iterators either run under the lock or use RCU and restart if the list changes. `get_singleton()` returns NULL, a single fence, or a newly created fence array. Wait/test/deadline operations iterate matching usage fences without requiring callers to hold the lock.

State and persistence behavior: each reservation object owns its fence list references until replaced or finalized. Signaled fences are lazily pruned during reservation/growth. Usage tags determine which fences block read/write/kernel/bookkeeping operations.

Dependencies and integration points: depends on dma-fence core, fence arrays for singleton aggregation, ww_mutex wound/wait locking, RCU, mm and mmu-notifier lockdep priming, and seq_file debug descriptions. Used by dma-buf core, DRM GEM objects, sync-file import/export, and shared buffer exporters/importers.

Risks and test signals: callers must reserve slots before adding fences and hold the reservation lock for mutations. Pointer low-bit packing assumes fence pointer alignment. Unlocked iteration can restart, so accumulation code must handle `dma_resv_iter_is_restarted()`. Test signals include all usage levels, slot reservation compaction, replacing fences by context, RCU iteration under concurrent updates, singleton array creation, wait timeout semantics, deadline forwarding, and lockdep init coverage for reclaim/mmu-notifier interactions.
