# sources/distributed-fs/ceph-client/drivers/infiniband/core/rw.c

## Purpose
`rw.c` builds and tears down RDMA READ/WRITE work request chains for upper-layer protocols. It chooses among direct single SGE, multiple direct SGEs, fast-registered memory regions, signature/integrity memory regions, and a bvec IOVA coalescing path.

## Important APIs, types, and functions
- Public initialization APIs: `rdma_rw_ctx_init()`, `rdma_rw_ctx_init_bvec()`, and `rdma_rw_ctx_signature_init()`.
- Posting APIs: `rdma_rw_ctx_wrs()` returns the send WR chain, and `rdma_rw_ctx_post()` posts it.
- Cleanup APIs: `rdma_rw_ctx_destroy()`, `rdma_rw_ctx_destroy_bvec()`, and `rdma_rw_ctx_destroy_signature()`.
- Queue sizing/pool APIs: `rdma_rw_mr_factor()`, `rdma_rw_max_send_wr()`, `rdma_rw_init_qp()`, `rdma_rw_init_mrs()`, and `rdma_rw_cleanup_mrs()`.
- Internal modes are `RDMA_RW_SINGLE_WR`, `RDMA_RW_MULTI_WR`, `RDMA_RW_MR`, `RDMA_RW_SIG_MR`, and `RDMA_RW_IOVA`.

## Control flow and behavior
For scatterlists, the code DMA maps an `sg_table`, skips to `sg_offset`, then decides whether RDMA READ/WRITE needs fast MRs. iWARP READs, `max_sgl_rd` overflow, and the `force_mr` module parameter drive the MR path. MR contexts pull MRs from QP pools, optionally prepend local invalidation, map pages into the MR, then chain register and RDMA WRs. If the MR path fails due to pool exhaustion in an optional optimization case, it falls back to direct SGEs.

For bvecs, the code validates input, uses MR registration for iWARP READ or forced MR, uses a single mapped bvec for one segment, and otherwise tries the two-step DMA IOVA allocator to create a contiguous DMA span represented by one SGE. If IOVA is unavailable it maps each bvec as direct SGEs. Signature initialization maps data and protection SGs, pulls a signature MR, maps PI data, and emits `IB_WR_REG_MR_INTEGRITY` followed by RDMA READ/WRITE.

## State, persistence, and dependencies
`struct rdma_rw_ctx` persists all temporary DMA mappings, SGE arrays, WR arrays, MR pool references, IOVA state, and context type until the matching destroy function is called. QPs own `rdma_mrs` and `sig_mrs` pools. The lkey is intentionally updated in `rdma_rw_ctx_wrs()` just before posting to avoid invalidation state changes for initialized but never posted contexts.

## Integration points
The file integrates with block/storage upper-layer protocols using `rdma/rw.h`, DMA mapping APIs, PCI P2PDMA-capable bvec mapping, MR pools, QP creation sizing, integrity offload, and low-level verbs posting through `ib_post_send()`.

## Risks and test signals
Risks include mismatched init/destroy variants, DMA unmap count mistakes after bvec coalescing, MR pool leaks on partial failure, iWARP correctness regressions if MR fallback is used incorrectly, lkey invalidation ordering bugs, and overflow in combined SGE/WR allocations. Test signals include READ and WRITE with one SG, many SGs, offsets, iWARP, forced MR, MR pool exhaustion, bvec IOVA available/unavailable, P2PDMA pages, signature offload, queue sizing assertions, and fault injection through DMA map and MR pool allocation.
