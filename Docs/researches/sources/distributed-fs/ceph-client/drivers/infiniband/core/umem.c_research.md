# sources/distributed-fs/ceph-client/drivers/infiniband/core/umem.c

## Purpose

`umem.c` implements the core userspace memory pinning and DMA mapping helper for RDMA user memory registrations. It creates `struct ib_umem` objects from virtual address ranges, enforces memlock accounting, pins pages with long-term GUP, builds scatter-gather tables, maps them for device DMA, releases and dirties pages, chooses a hardware page size, and copies data out of a registered UMEM.

## Important APIs, Types, and Functions

- `ib_umem_get` is the main constructor for non-ODP, non-dmabuf user memory. It validates the address range, checks `RLIMIT_MEMLOCK`, pins pages, creates an append SG table, maps the SG table for DMA, and returns `struct ib_umem`.
- `ib_umem_release` dispatches release to dmabuf or ODP helpers when needed, otherwise unmaps DMA, unpins pages, decrements `mm->pinned_vm`, drops the owning `mm_struct`, and frees the UMEM.
- `ib_umem_find_best_pgsz` computes the largest compatible hardware page size from a device page-size bitmap, the UMEM scatterlist, and the requested IOVA.
- `ib_umem_copy_from` copies data from the UMEM SG table into a kernel destination buffer using `sg_pcopy_to_buffer`.
- `__ib_umem_release` is the shared release helper for DMA unmapping, dirty accounting, page unpinning, and SG table freeing.

## Control Flow

`ib_umem_get` first rejects arithmetic overflow and unsupported on-demand access. It requires `can_do_mlock`, allocates and initializes `struct ib_umem`, grabs the current mm, and allocates a temporary page-pointer array. It computes page count from the aligned address range and charges `mm->pinned_vm`; non-privileged callers exceeding `RLIMIT_MEMLOCK` fail with `-ENOMEM`. It then loops over the range using `pin_user_pages_fast` with `FOLL_LONGTERM` and optional `FOLL_WRITE`, appending pages into `umem->sgt_append` with device maximum segment sizing. After all pages are pinned, it calls `ib_dma_map_sgtable_attrs` with coherent and optional weak-ordering DMA attributes. On errors it unpins what was already pinned, rolls back memlock accounting, drops the mm, and frees memory.

`ib_umem_find_best_pgsz` is used after mapping. For ODP UMEMs it returns the ODP page size if supported. For normal UMEMs it tracks virtual and DMA discontinuities and builds a bit mask of address bits that cannot vary within a hardware page. The selected page size is the largest supported power-of-two page size compatible with the virtual address, physical DMA layout, first-page offset, and total length.

Release unmaps the DMA table when dirty, unpins every page range with dirty marking if writable, periodically reschedules, frees the append SG table, and decrements pinned pages from the owning mm.

## State and Persistence

UMEM state is runtime only and tied to driver-created RDMA objects such as memory regions. It stores address, length, IOVA, writable flag, owning mm, DMA attributes, SG table, and mode flags (`is_dmabuf`, `is_odp`). Persistent effects are limited to mm pinned-page accounting and page dirty state on release. `mmgrab`/`mmdrop` preserve the mm while the UMEM exists.

## Dependencies and Integration Points

This file integrates with Linux GUP/pinning APIs, scatter-gather append tables, DMA mapping APIs, mm accounting, RDMA access-flag helpers, ODP/dmabuf release helpers, and driver operations such as `reg_user_mr` that consume `struct ib_umem`. It also relies on `ib_dma_max_seg_size` for SG construction and `ib_dma_map_sgtable_attrs` for IOMMU/device mapping.

## Risks

Long-term page pinning is high risk for memory-management correctness. Bugs can leak pinned pages, underflow `pinned_vm`, dirty pages incorrectly, or allow unprivileged callers to bypass memlock limits. Address arithmetic and page-count overflow are explicitly checked and should remain covered. DMA map failures after partial pinning require exact unwinding. Page-size selection mistakes can cause hardware page tables to alias or split incorrectly. Since ODP and dmabuf are dispatched through `ib_umem_release`, mode flags must be set consistently by alternate constructors.

## Test Signals

Useful tests include registering and deregistering writable/read-only MRs, memlock-limit enforcement, unaligned address and length ranges, huge SG lists, DMA map failure injection, ODP and dmabuf release dispatch, `ib_umem_find_best_pgsz` with physically contiguous and discontinuous SG entries, and `ib_umem_copy_from` boundary checks. Kernel leak detection should show no pinned-page or SG table leaks after failure paths.
