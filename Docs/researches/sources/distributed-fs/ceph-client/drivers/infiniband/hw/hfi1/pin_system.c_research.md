# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pin_system.c

## Purpose
`pin_system.c` implements system-memory page pinning for HFI1 user SDMA. It caches pinned user virtual-address ranges in the driver's MMU red-black tree so SDMA descriptors can safely reference user pages while also reacting to mmu-notifier invalidation and pin-limit pressure.

## Important APIs, Types, And Functions
`struct sdma_mmu_node` extends `mmu_rb_node` with the owning user SDMA packet queue, an array of pinned `struct page *`, and a page count. `hfi1_init_system_pinning()` registers queue-specific `mmu_rb_ops`; `hfi1_free_system_pinning()` unregisters them. `pin_system_pages()` enforces pin limits through `hfi1_can_pin_pages()`, evicts cached nodes when needed, calls `hfi1_acquire_user_pages()`, and increments `pq->n_locked`. `get_system_cache_entry()` finds, prepends, or creates cache nodes for a request range. `add_mapping_to_sdma_packet()` converts cached pages into SDMA descriptors with node get/put callbacks. `hfi1_add_pages_to_sdma_packet()` is the exported packet-building entry point.

## Control Flow
For each user iovec segment, the code aligns the requested range to page boundaries and searches the mmu-rb cache. If an existing node covers the start, it is returned with an extra safety kref. If the first matching node begins after the requested start, a new prepended node is pinned and inserted. If no node exists, the entire aligned range is pinned and inserted. Packet construction then walks page by page, computing page offsets and byte counts, and attaches the last descriptor for each cache-entry span to the node context so descriptor completion releases the kref. The top-level loop advances `req->iov_idx`, iovec offsets, and remaining packet bytes.

## State And Persistence
Pinned ranges live in per-queue mmu-rb nodes until evicted, invalidated, or queue teardown. `pq->n_locked` tracks the number of pages locked by the queue. Each cache node has a tree reference plus transient safety and descriptor references. There is no disk or firmware persistence; state is tied to the process `mm_struct`, the user SDMA queue, and outstanding descriptors.

## Dependencies And Integration Points
The implementation depends on `mmu_rb`, HFI1 user-page acquire/release helpers, queue pin accounting, user SDMA request/iovec/txreq structures, `sdma_txadd_page()`, krefs, mmu notifier release paths, and trace/debug macros. It is the bridge between user SDMA packet assembly and Linux memory-management invalidation.

## Risks
The code has subtle kref lifetime rules: successful cache lookup and insertion deliberately take a safety reference that must be released after descriptor assignment. A mismatch would leak pinned pages or free nodes still referenced by descriptors. `pin_system_pages()` passes `node->npages` as the start offset when unpinning a partial pin failure, but `node->npages` is still zero for new nodes, which appears intentional but deserves regression coverage. Concurrent insertion races are handled by retrying `-EEXIST`; invalidation during descriptor construction is protected by references but should be stress tested.

## Test Signals
Exercise empty ranges, unaligned iovecs spanning many pages, cache hits, prepended cache nodes, concurrent insertion races, pin-limit eviction, partial pin failures, mmu invalidation while descriptors are being built, descriptor callback release, queue teardown with live nodes, and accounting of `n_locked` after success and failure.
