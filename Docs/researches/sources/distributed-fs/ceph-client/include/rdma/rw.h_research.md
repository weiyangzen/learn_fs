# sources/distributed-fs/ceph-client/include/rdma/rw.h

Purpose: Defines the RDMA READ/WRITE context abstraction that maps block or scatterlist I/O into send work requests, optionally using memory registration or signature offload.

Important APIs/types/functions: `struct rdma_rw_ctx` records operation count and mapping type, with variants for a single SGE, multiple SGEs, IOVA-based bvec mapping, or a registration context containing RDMA WR, REG WR, invalidate WR, MR, and SG table. APIs include `rdma_rw_ctx_init()`, `rdma_rw_ctx_destroy()`, bvec variants, signature variants, `rdma_rw_ctx_wrs()`, `rdma_rw_ctx_post()`, MR sizing helpers, QP initialization, MR pool initialization, and cleanup.

Control flow and state: Callers initialize a context from SG/bvec input, obtain or post the generated WR chain, then destroy the context to unmap DMA and release MRs. The `type` field selects which union branch is valid; `nr_ops` excludes MR management WRs. Signature contexts additionally include protection SG lists and `ib_sig_attrs`.

Dependencies and integration: Integrates RDMA core verbs, RDMA CM, MR pools, DMA mapping, scatterlists, bio vectors, and block/storage clients such as NVMe/RDMA or SCSI RDMA transports.

Risks and test signals: Risks include mismatched init/destroy direction or SG counts, leaking MRs, invalid DMA unmap lengths, WR chain ordering with local invalidation, and underestimating send WR needs. Tests should cover single-SGE, multi-SGE, bvec IOVA, registration-backed transfer, signature offload, bidirectional error unwind, and QP attr sizing.
