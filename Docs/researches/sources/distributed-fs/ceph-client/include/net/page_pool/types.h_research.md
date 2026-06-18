# sources/distributed-fs/ceph-client/include/net/page_pool/types.h

Purpose: defines page_pool flags, parameters, allocation/recycle stats, memory-provider parameters, the internal `struct page_pool`, and core allocation/destruction prototypes.

Important APIs and types: flags cover DMA mapping, sync-for-device, system pools, and unreadable netmem. `struct page_pool_params` separates hot `fast` fields from slow/control fields such as netdev and queue index. `struct pp_alloc_cache` is the NAPI-side cache. `struct page_pool` stores fast params, CPU/NAPI assumptions, fragment state, delayed release work, stats, XDP memory ID, cache, ptr_ring recycle store, memory provider hooks, DMA xarray, release counters, user refcount, destroy counter, and user-visible ID/list state. Prototypes allocate pages/netmem/frags, create pools, destroy, attach XDP memory, bulk put, and update NUMA node.

Control flow: drivers create one pool per RX queue/NAPI context, allocate from cache/ring/page allocator or provider, recycle through cache/ring/release paths, and destroy after in-flight pages drain.

State and persistence: state is runtime pool memory and DMA mappings; user-facing IDs aid diagnostics but do not persist.

Dependencies and integration points: depends on DMA direction, ptr_ring, xarray, netmem, NAPI, XDP, workqueues, and optional stats.

Risks and test signals: risks include violating single-consumer allocation assumptions, ptr_ring producer/consumer races, lingering in-flight pages during destroy, incorrect flags with unreadable netmem, and stats cacheline contention. Test per-RX-queue pools, high-order pages, NUMA changes, XDP mem disconnect, bulk return, stats, memory-provider pools, and CONFIG_PAGE_POOL disabled stubs.
