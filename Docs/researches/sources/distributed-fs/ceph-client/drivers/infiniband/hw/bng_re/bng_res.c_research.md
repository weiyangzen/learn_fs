<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.c

## Purpose
Implements low-level resource allocation for `bng_re`: coherent DMA stats memory and paged hardware queues with 0-, 1-, or 2-level page-block-list indirection.

## Important APIs, Types, And Functions
- `bng_re_alloc_stats_ctx_mem()` allocates coherent DMA memory sized by `bng_re_chip_ctx.hw_stats_size`, initializes `fw_id` to invalid, and stores DMA address/size.
- `bng_re_free_stats_ctx_mem()` frees coherent stats memory if present, clears the structure, and restores invalid firmware id.
- `bng_alloc_pbl()` allocates arrays of virtual pointers and DMA addresses, then allocates each coherent page/block for a PBL level unless `sginfo->nopte` is set.
- `bng_free_pbl()` frees all coherent pages tracked by a PBL and the vmalloc arrays.
- `bng_re_alloc_init_hwq()` computes queue page needs, allocates the required PBL levels, fills DMA PTE/PDE entries with `PTU_PTE_VALID`, marks last and next-to-last queue pages, initializes hardware queue indices, element size, page-entry counts, direct-access pointers, and lock.
- `bng_re_free_hwq()` releases all allocated PBL levels and resets queue metadata.

## Control Flow
Stats allocation is a simple coherent DMA allocation path. Hardware queue allocation rounds requested depth and stride up to powers of two, computes pages from depth * stride / page size, and chooses a PBL layout. A single page without `nopte` uses level 0 directly. Up to 512 pages uses one indirection level: level 0 contains PTEs pointing to level 1 pages. More than 512 pages uses two indirection levels: level 0 contains PDEs pointing to level 1 PBL pages, and level 1 contains PTEs pointing to level 2 data pages.

On every PBL allocation failure, control jumps to `fail`, which calls `bng_re_free_hwq()` to release any partial allocations. On success, queue indices are zeroed, hardware queue metadata is assigned, and `pbl_ptr`/`pbl_dma_ptr` are set to the level containing directly addressable queue entries.

## State And Persistence
Persistent state is held in `struct bng_re_hwq`: PCI device, lock, PBL arrays for each level, current level, direct PBL pointers, max elements, requested depth, element size, producer/consumer indices, and queue entries per page. PBL structures persist coherent page pointers, DMA mappings, page count, and page size until `bng_re_free_hwq()`.

## Dependencies And Integration Points
Depends on Linux PCI DMA coherent allocation, vmalloc, power-of-two rounding, RDMA umem headers, BNGE HSI constants, and `bng_roce_hsi.h` PTE flags. Firmware allocation in `bng_fw.c` relies on these functions for CMDQ and CREQ storage. Stats memory is used by `bng_dev.c` and firmware initialization.

## Risks And Edge Cases
The allocator rounds depth and stride for memory sizing but later sets `hwq->max_elements = hwq->depth`, where `hwq->depth` is the original requested depth, while macros such as `HWQ_CMP()` assume power-of-two `max_elements`. This is safe only if callers already request power-of-two depths; otherwise ring math can break. `bng_re_free_hwq()` returns early if `level >= BNG_PBL_LVL_MAX`, which can skip partial allocations if level was not lowered before a later allocation failure. `nopte` paths skip data-page allocation and alter direct-access level selection, so callers must supply externally backed pages consistently.

## Test Signals
Allocation tests should cover 0-page rejection, one-page level 0, small multi-page level 1, large level 2, `nopte` cases, and injected failures at every PBL allocation stage. DMA debug should show all coherent allocations freed. Runtime CREQ/CMDQ operation validates `pbl_ptr`, `pbl_dma_ptr`, producer/consumer math, and last-page PTE flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.c -->
