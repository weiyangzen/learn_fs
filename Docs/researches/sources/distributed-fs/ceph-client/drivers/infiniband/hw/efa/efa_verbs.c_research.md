# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_verbs.c

Implements EFA RDMA core verbs and custom uverbs: device/port queries, PD/UAR allocation, QP/CQ creation and destruction, QP state changes, MR registration including dmabuf, mmap, AH management, hardware stats, and MR interconnect-ID query.

Important functions include `efa_query_device`, `efa_alloc_ucontext`, `efa_create_qp`, `efa_modify_qp`, `efa_create_user_cq`, `efa_reg_mr`, `efa_reg_user_mr_dmabuf`, `efa_dereg_mr`, `efa_mmap`, `efa_create_ah`, `efa_get_hw_stats`, and `UVERBS_HANDLER(EFA_IB_METHOD_MR_QUERY)`. PBL helpers build inline, continuous, or indirect chained page lists for MR registration.

Control flow validates userspace ABI padding and caps, allocates DMA/kernel backing when needed, posts an admin command, installs mmap or xarray entries, copies response data to userspace, then unwinds acquired resources on failure. CQ creation supports external contiguous `ib_umem` or driver-allocated memory and optional EQ-backed completion channels. QP creation exposes doorbells, LLQ descriptors, and optional RQ memory through RDMA mmap entries.

Persistent state includes PDN, UARN, QP handles/QPN/state/caps/RQ DMA buffers, CQ indices/DMA/EQ association, MR umem/lkey/rkey/interconnect IDs, AH handles, mmap entries, CQ xarray entries, and stats counters. Dependencies include RDMA core, uverbs, DMA/umem/dmabuf, xarray, EFA admin commands, and EFA IO descriptor definitions.

Risks include ABI padding mistakes, mmap lifetime leaks, DMA mapping failures, incomplete unwind after hardware object creation, interrupt races during CQ destruction, PBL chunk chaining errors, and divergent SRD vs UD QP transition rules. Test signals include provider tests, QP/CQ create-destroy with and without completion channels, mmap paths, QP state matrix tests, inline/indirect MR registration, dmabuf MR registration, AH lifecycle, and stats reads.
