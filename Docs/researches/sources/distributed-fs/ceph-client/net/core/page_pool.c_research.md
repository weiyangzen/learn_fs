<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool.c -->
# sources/distributed-fs/ceph-client/net/core/page_pool.c

## Purpose
Core page-pool allocator/recycler for high-speed RX and XDP paths. It provides per-pool allocation caches, DMA mapping lifetime management, recycling rings, fragment allocation, memory-provider integration, delayed destruction, and optional statistics.

## APIs, Types, and Functions
Creation APIs are `page_pool_create_percpu()` and `page_pool_create()`. Allocation APIs are `page_pool_alloc_netmems()`, `page_pool_alloc_pages()`, `page_pool_alloc_frag_netmem()`, and `page_pool_alloc_frag()`. Return APIs are `page_pool_put_unrefed_netmem()`, `page_pool_put_unrefed_page()`, and `page_pool_put_netmem_bulk()`. Lifecycle and metadata APIs include `page_pool_destroy()`, `page_pool_update_nid()`, `page_pool_enable_direct_recycling()`, `page_pool_disable_direct_recycling()`, `page_pool_use_xdp_mem()`, `page_pool_set_pp_info()`, `page_pool_clear_pp_info()`, and netmem provider helpers for `net_iov`. Stats helpers are exported when `CONFIG_PAGE_POOL_STATS` is enabled.

## Control Flow, State, and Persistence
Initialization validates flags, DMA direction/sync requirements, ring size, high-order limits, memory-provider callbacks, stats allocation, and xarray setup for DMA mapping indexes. Allocation first uses the lockless alloc cache, refills from the ptr_ring with NUMA checks, and falls back to bulk page allocation or provider allocation. New pages are optionally DMA-mapped, tagged with PageNetpp/page-pool metadata, optionally initialized by callback, and counted in `pages_state_hold_cnt`. Return checks refcounts and pfmemalloc status, syncs for device if needed, recycles directly to the NAPI-local cache when safe, otherwise produces to the ptr_ring, and finally releases DMA/provider state and puts pages if recycling is impossible. Destruction disables direct recycling, drains fragment state, scrubs alloc cache/ring/DMA xarray, checks inflight count against release count, and retries with delayed work until outstanding pages return.

## Dependencies and Integration
Depends on DMA mapping APIs, `ptr_ring`, xarray, page flags, NAPI ownership, XDP memory IDs, netmem/net_iov abstractions, page-pool memory providers, netdev locks for provider-backed pools, tracepoints, and page-pool user listing from `page_pool_user.c`.

## Risks and Test Signals
Risks include refcount/inflight mismatches causing delayed destroy stalls, races between DMA sync and scrub, direct recycling under PREEMPT_RT or wrong NAPI context, compressed DMA address/index overflow, provider ops outside rodata, high-order allocation limitations, and fragment bias accounting errors. Test signals are fast/slow allocation stats, DMA map/unmap count balance, bulk return with mixed pools, fragment drain at page boundaries, NUMA update flushing alloc cache, destruction retry warnings for leaked pages, provider alloc/release paths, and error injection on `page_pool_alloc_netmems()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool.c -->
