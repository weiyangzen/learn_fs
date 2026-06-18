# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_pages.c

## Purpose
`user_pages.c` centralizes long-term user page pinning policy for hfi1 send/receive caches. It enforces RLIMIT_MEMLOCK and a driver cache-size module parameter, pins pages with long-term GUP, updates `mm->pinned_vm`, and releases pages with dirty tracking.

## Important APIs and Functions
`hfi1_can_pin_pages(struct hfi1_devdata *, struct mm_struct *, u32 nlocked, u32 npages)` decides whether a cache may pin additional pages. `hfi1_acquire_user_pages(struct mm_struct *, unsigned long vaddr, size_t npages, bool writable, struct page **pages)` calls `pin_user_pages_fast()` with `FOLL_LONGTERM` and optional `FOLL_WRITE`, then increments `pinned_vm` by the actual pin count. `hfi1_release_user_pages(struct mm_struct *, struct page **, size_t npages, bool dirty)` calls `unpin_user_pages_dirty_lock()` and decrements `pinned_vm` when an `mm` is available. The `cache_size` module parameter defaults to 256 MB.

## Control Flow
Expected receive or SDMA cache code first calls `hfi1_can_pin_pages()` with its current locked-page count. Non-`CAP_IPC_LOCK` callers must fit both the process RLIMIT and a per-user-context quarter-RLIMIT share. All callers must fit the driver cache-size cap. If allowed, pages are pinned and accounted. Release reverses pinning and accounting; close paths may pass `mm == NULL` after signal teardown.

## State, Persistence, and Dependencies
State is global module parameter `cache_size` and per-mm `pinned_vm`; callers retain their own `nlocked` counters. Dependencies are Linux mm, capabilities, rlimits, and long-term GUP APIs. The policy assumes one process per context and one cache per context, as noted by comments.

## Integration Points
`user_exp_rcv.c` calls these functions when programming expected receive TIDs. User SDMA pinning code also uses the same policy through pinning helpers. Correct accounting is essential for MMU notifier cleanup and memory pressure behavior.

## Risks and Test Signals
Risks include partial GUP success requiring caller cleanup, mismatch between actual pinned count and requested count, stale `nlocked` accounting in callers, RLIMIT division by user-context count assumptions, and long-term pins on memory types that GUP rejects. Test signals include memlock-limit failures, CAP_IPC_LOCK bypass, cache-size-limit failures, partial pin cleanup, dirty release on receive buffers, and no `pinned_vm` leak after process exit.
