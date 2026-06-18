# sources/distributed-fs/ceph-client/include/rdma/iter.h

Purpose: Provides RDMA block DMA iterators for walking DMA-mapped scatterlists and `ib_umem` memory in hardware page-size aligned blocks.

Important APIs/types/functions: `struct ib_block_iter`, `__rdma_block_iter_start`, `__rdma_block_iter_next`, `rdma_block_iter_dma_address`, `rdma_for_each_block`, `__rdma_umem_block_iter_start`, `__rdma_umem_block_iter_next`, and `rdma_umem_for_each_dma_block`.

Control flow: Callers start an iterator with an SGL and page size, then loop while the internal next function advances through aligned DMA blocks. The umem variant seeds from `umem->sgt_append.sgt`, adjusts for `ib_umem_offset`, and limits iterations to `ib_umem_num_dma_blocks`.

State and persistence behavior: Iterator fields are caller-local runtime state. The header does not own mappings or references; the SGL/umem must stay valid and DMA mapped.

Dependencies and integration points: Depends on Linux scatterlists and `rdma/ib_umem.h`. Integrates with MR registration and hardware page-list programming paths.

Risks: Bad page-size selection, stale SGL entries, or wrong `nents` can emit invalid DMA addresses. The umem loop relies on the caller following `ib_umem_find_best_pgsz`/`ib_umem_num_dma_blocks` semantics.

Test signals: Multi-entry SGLs, contiguous DMA coalescing, unaligned umem addresses, boundary page sizes, and exact iteration-count checks.
