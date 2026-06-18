# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_alloc.c

Purpose: Provides shared DMA buffer allocation helpers and global ID/table cleanup for HNS RoCE resources.

Important APIs/types/functions: `hns_roce_buf_alloc()` allocates a `struct hns_roce_buf` made of one or more coherent DMA trunks. `hns_roce_buf_free()` releases those trunks. `hns_roce_get_kmem_bufs()` exports kernel buffer DMA page addresses; `hns_roce_get_umem_bufs()` exports user umem DMA blocks. `hns_roce_cleanup_bitmap()` tears down ID allocators and xarrays for XRC, SRQ, QP, CQ, MR, PD, and UAR resources.

Control flow: Allocation validates that the requested page shift is at least hardware page size. Direct mode requests one contiguous trunk aligned to page size; non-direct mode allocates one trunk per hardware page-sized unit. `NOFAIL` mode accepts partial allocation as long as at least one trunk was allocated; otherwise all trunks must be allocated. On failure it frees all allocated trunks.

State and persistence: Buffer objects persist until explicit free and own coherent DMA mappings in `trunk_list`. ID allocator cleanup is device-lifetime teardown state and must happen after resource users are gone.

Dependencies and integration: Uses coherent DMA APIs, RDMA umem block iteration, IDA, xarray cleanup, and table cleanup functions implemented by QP/CQ code. The buffer layout is consumed by MTR/MR/CQ/QP creation through `hns_roce_buf_dma_addr()`.

Risks: Partial `NOFAIL` buffers require consumers to honor `npages` and allocated size. `page_shift > trunk_shift` in `hns_roce_get_kmem_bufs()` is rejected because it would skip beyond trunk granularity. Test signals include direct/non-direct allocation, atomic allocation flags, partial allocation handling, DMA address enumeration, and teardown under all optional caps.
