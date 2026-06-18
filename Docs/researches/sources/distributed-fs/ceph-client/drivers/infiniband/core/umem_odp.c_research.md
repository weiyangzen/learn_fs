# sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_odp.c

## Purpose

`umem_odp.c` implements On-Demand Paging UMEM support for RDMA. Unlike normal UMEM, ODP does not pin and map all pages at registration time. It records an address range, owning mm, page granularity, HMM DMA map, and MMU interval notifier so drivers can fault and map pages as hardware needs them, then unmap them on invalidation or release.

## Important APIs, Types, and Functions

- `ib_umem_odp_get` creates an explicit ODP UMEM for a user virtual range and access flags.
- `ib_umem_odp_alloc_implicit` creates an implicit parent ODP UMEM that has no fixed VA range and exists to hold process/mm context for child UMEMs.
- `ib_umem_odp_alloc_child` creates an explicit child range under an implicit parent.
- `ib_init_umem_odp` initializes locking, address alignment, HMM DMA map storage, and `mmu_interval_notifier`.
- `ib_umem_odp_map_dma_and_lock` faults/maps a requested range, validates MMU notifier sequence, and returns with `umem_mutex` held on success for driver page-table updates.
- `ib_umem_odp_unmap_dma_pages` unmaps DMA PFNs in a range, dirties writable pages, decrements mapped page count, and clears HMM flags.
- `ib_umem_odp_release` frees explicit mappings/notifiers or implicit parent state.

## Control Flow

Explicit ODP creation requires `IB_ACCESS_ON_DEMAND`, allocates `struct ib_umem_odp`, stores current mm and task group pid, chooses `PAGE_SHIFT` or `HPAGE_SHIFT` for hugepage access, and calls `ib_init_umem_odp`. Initialization aligns the range to the ODP page size, checks for overflow and zero-sized maps, allocates either a virtual-DMA PFN list or an HMM DMA map, and inserts an interval notifier covering the aligned address range. Child allocation is similar but inherits device, writable flag, and mm from the implicit root and temporarily obtains `mmget_not_zero` because notifier insertion requires a live mm reference.

Mapping starts by verifying the requested range lies inside the UMEM. It resolves the owning process from the saved TGID and obtains an mm reference. It prepares an `hmm_range` over the aligned fault range, optionally requests fault and write access, points the range at the UMEM PFN slice, and retries `hmm_range_fault` on temporary `-EBUSY` until timeout. After HMM returns, it locks `umem_mutex` and checks `mmu_interval_read_retry`; if invalidation raced, it unlocks and retries. It scans PFNs, skips invalid/already-DMA-mapped entries, rejects unexpectedly small HMM mapping order relative to the UMEM page shift, and returns the number of ODP pages mapped while keeping `umem_mutex` held. The caller is responsible for unlocking after programming hardware.

Release of explicit UMEMs locks `umem_mutex`, unmaps the whole range, removes the interval notifier, frees the HMM map, drops the PID reference, and frees memory. Implicit UMEMs skip notifier/map teardown because they never registered a range.

## State and Persistence

State is runtime and attached to RDMA memory registration lifetime: address, length, owning mm, TGID pid, page shift, HMM PFN list/map, interval notifier sequence, mapped page count, and mutex. Persistence side effects are page dirtying on unmap and MMU notifier registration while active.

## Dependencies and Integration Points

The file depends on Linux HMM, MMU interval notifiers, mm lifetime APIs, hugetlb configuration, RDMA UMEM mode dispatch, and driver ODP fault handlers. Drivers provide notifier ops and call `ib_umem_odp_map_dma_and_lock` when hardware faults require page table population, then use `ib_umem_odp_unmap_dma_pages` during invalidation handling.

## Risks

ODP is concurrency-heavy. Important races include mm teardown, process exit, MMU invalidation during HMM fault, and driver hardware access during unmap. Correct use of `umem_mutex`, notifier sequence retry, `mmget_not_zero`, and release ordering is critical. Returning with a lock held on success is an unusual API contract that callers must follow exactly. Hugepage page-shift mismatches can produce mapping errors. Dirtying writable pages without page locks relies on `umem_mutex` preventing concurrent notifier progress, which should be reviewed carefully when changing invalidation behavior.

## Test Signals

Signals include explicit and implicit ODP MR registration, child allocation after parent creation, invalid ranges and overflow rejection, process-exit behavior, HMM retry on `-EBUSY`, invalidation racing a fault, hugepage access, writable page dirtying on unmap, mapped-page count balance, and lockdep validation around `umem_mutex` in reclaim/notifier contexts. Driver ODP page-fault tests should verify the caller unlocks only after page-table updates.
