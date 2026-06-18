# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/odp.c

## Purpose

`odp.c` implements mlx5 On-Demand Paging support for InfiniBand memory. It populates and invalidates hardware translation tables for ODP MRs, handles explicit, implicit, dmabuf, WQE, RDMA, and memory-scheme page faults, manages the page-fault event queue, advertises ODP capabilities, and implements `advise_mr` prefetch behavior.

The file coordinates three subsystems that must agree under concurrency: Linux MMU interval notifiers and HMM DMA mapping, mlx5 UMR translation-table updates, and asynchronous hardware page-fault events. It also supports implicit ODP by building a two-level translation scheme: a top-level KSM implicit MR points to child MTT MRs that cover large chunks of process address space.

## Important APIs, Types, and Functions

Primary entry points:

- `mlx5_odp_populate_xlt()` fills either MTT entries or KSM entries during UMR updates.
- `mlx5_ib_alloc_implicit_mr()` creates a full-address-space implicit ODP MR.
- `mlx5_ib_free_odp_mr()` releases implicit child MRs and private null MKeys.
- `mlx5_ib_init_odp_mr()` snapshots/prefaults an explicit ODP MR during registration.
- `mlx5_ib_init_dmabuf_mr()` maps and enables dmabuf translations.
- `mlx5r_odp_create_eq()` lazily creates the page-fault EQ, workqueue, notifier, and mempool.
- `mlx5_ib_odp_init_one()`, `mlx5_ib_odp_cleanup_one()`, and `mlx5_ib_odp_init()` initialize device and global ODP state.
- `mlx5_ib_advise_mr_prefetch()` implements synchronous or asynchronous `advise_mr` prefetch.

Important internal types and helpers:

- `struct mlx5_pagefault` normalizes RDMA, WQE, and memory page-fault EQE payloads.
- `populate_mtt()` maps valid HMM PFNs to DMA addresses and builds MTT entries.
- `populate_ksm()` builds implicit KSM entries pointing at child MRs or null MKeys.
- `mlx5_ib_invalidate_range()` is the MMU interval notifier invalidation callback.
- `implicit_get_child_mr()`, `destroy_unused_implicit_child_mr()`, and `free_implicit_child_mr_work()` manage implicit child MR creation and deferred destruction.
- `pagefault_real_mr()`, `pagefault_implicit_mr()`, `pagefault_dmabuf_mr()`, and `pagefault_mr()` map pages and issue UMR translation updates.
- `find_odp_mkey()` resolves fault MKeys from `dev->odp_mkeys` with reference protection.
- `pagefault_single_data_segment()` walks direct and indirect MKeys for a data segment.
- `mlx5_ib_mr_wqe_pfault_handler()`, `mlx5_ib_mr_rdma_pfault_handler()`, and `mlx5_ib_mr_memory_pfault_handler()` resolve the three page-fault subtypes.

## Control Flow

During initialization, `mlx5_ib_odp_init()` derives implicit MR geometry from `TASK_SIZE`: child MTT coverage is 1 GiB for common 48-bit address spaces or 16 GiB for 56-bit address spaces. `mlx5_ib_odp_init_one()` fills ODP capabilities from hardware support for page-granular access, UMR, transport-specific ODP operations, null MKeys, fixed buffer size, and indirect MKeys. The page-fault EQ is created lazily by MR registration through `mlx5r_odp_create_eq()`.

ODP translation updates call `mlx5_odp_populate_xlt()`. MTT population skips zap operations, maps valid HMM PFNs through `hmm_dma_map_pfn()`, sets read/write bits, and increments `odp->npages`. KSM population for implicit ODP installs child MR lkeys when present and null MKeys otherwise. The KSM update path requires `umem_mutex` to pair xarray changes with hardware translation updates.

Invalidation starts from `mlx5_ib_invalidate_range()`. The callback refuses non-blockable ranges, locks `umem_mutex`, updates the interval sequence, scans valid PFNs overlapping the invalidation range, zaps aligned blocks of MTT entries with atomic UMR updates, updates ODP invalidation stats, unmaps DMA pages, and schedules destruction of now-empty implicit child MRs.

Page-fault handling begins in the EQ interrupt notifier. `mlx5_ib_eq_pf_process()` drains EQEs, allocates `mlx5_pagefault` objects from a mempool, decodes subtype-specific fields, and queues work on a high-priority workqueue. Worker code dispatches to WQE, RDMA, or memory-scheme handlers and always resumes the hardware fault with success or error unless the event protocol says only the last memory-fault fragment should resume.

WQE faults hold the QP/SRQ resource, copy the relevant WQE, parse transport-specific headers to find data segments, and call `pagefault_data_segments()`. RDMA faults map the rkey/address range needed for forward progress, resume the QP, then optionally prefetch more. Memory-scheme faults resolve the MKey directly, map a prefetch window if possible, fall back to the demanded range, and resumes only on `MLX5_MEMORY_PAGE_FAULT_FLAGS_LAST`.

`pagefault_single_data_segment()` handles direct ODP MRs and indirect MKeys/MWs. Direct MRs are mapped by `pagefault_mr()`. Indirect keys are queried with `mlx5_core_query_mkey()`, converted into stack-like frames of KLM segments, and followed recursively up to the device `max_indirection` limit. Non-ODP MKeys are treated as already resident so mixed SGLs can progress.

Prefetch through `mlx5_ib_advise_mr_prefetch()` validates each lkey against the caller PD, checks write-prefetch permissions, then either maps synchronously when `IB_UVERBS_ADVISE_MR_FLAG_FLUSH` is set or queues async work that holds ODP MKey references until complete.

## State and Persistence Behavior

State is runtime-only. Global static geometry (`mlx5_imr_mtt_entries`, `mlx5_imr_ksm_entries`, page shifts, and MTT size) is computed once from virtual address width. Per-device state includes `dev->odp_caps`, `dev->odp_max_size`, `dev->odp_eq_mutex`, `dev->odp_pf_eq`, and `dev->odp_mkeys`.

Per-MR state lives in `mlx5_ib_mr`: ODP MRs store `umem`, `page_shift`, stats, implicit-child xarray, parent pointers, and optional null MKey. `ib_umem_odp` stores HMM PFN state, DMA mapping state, `npages`, notifier state, and a private backpointer to the MR. Reference counts on `mlx5_ib_mkey` protect objects while page-fault and prefetch workers are active.

Hardware state changes are translation-table updates: zap, enable, downgrade, indirect KSM updates, dmabuf page-size updates, and page-fault resume commands. The file treats MMU invalidation and page-fault repair as a synchronization protocol, using `umem_mutex`, dma-resv locks, xarray locks, and deferred work to avoid sleeping in invalidation-critical sections.

## Dependencies and Integration Points

`odp.c` depends on RDMA ODP core (`ib_umem_odp_*`), MMU interval notifiers, HMM and HMM DMA mapping, dma-buf reservation locks, pci p2pdma mapping state, mlx5 EQ APIs, mlx5 core resource holding for QPs/SRQs, WQE readers in `qp.c`, MKey creation and deregistration in `mr.c`, and UMR update APIs in `umr.c`.

It is integrated with `mr.c` registration paths: explicit ODP and dmabuf MRs are initialized here; implicit ODP MRs are allocated here; MKeys created in `mr.c` are stored in `dev->odp_mkeys` for lookup here. `main.c` uses `mlx5_ib_odp_init_one()` to advertise `.advise_mr` and cleanup destroys the ODP EQ.

## Risks and Edge Cases

Concurrency is the dominant risk. MMU invalidation can race with page faults, implicit child MR creation, child destruction, and MR deregistration. The code relies on strict ordering around xarray store/erase, `umem_mutex`, MKey refcounts, and hardware UMR updates. A missed reference or out-of-order KSM update can cause use-after-free or repeated hardware faults.

Fault handlers must resume hardware correctly. Returning success before enough bytes are mapped can corrupt forward progress, while failing to resume can stall a QP. RDMA faults with unknown length depend on packet-size prefetch heuristics. Memory-scheme faults have token and "last fragment" semantics that differ from transport faults.

Other edge cases include invalid virtual ranges, zero-length WQE segments meaning 2 GiB, nested indirect MKeys beyond `max_indirection`, non-ODP lkeys in mixed SGLs, dma-buf page-size changes after first fault, HMM PFNs without write access, p2pdma mapping failures, and implicit address-space geometry on architectures outside the handled VA sizes.

## Test Signals

High-value tests include ODP explicit MR page faults for read/write/atomic operations, implicit ODP over sparse address ranges, concurrent munmap/mprotect invalidation during RDMA traffic, nested MW/indirect MKey page faults, dmabuf page faults and invalidations, `advise_mr` prefetch with and without flush, and device cleanup while faults are outstanding. Runtime signals include ODP fault/prefetch/invalidation counters, page-fault resume errors, `-EAGAIN` retry paths, mempool/workqueue exhaustion, non-empty `odp_mkeys` at cleanup, and lockdep coverage for `umem_mutex` and dma-resv ordering.
