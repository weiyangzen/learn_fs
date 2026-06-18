# sources/distributed-fs/ceph-client/include/rdma/ib_umem.h

Purpose: defines RDMA user-memory registration objects and helpers for pinned user pages and dma-buf-backed memory, with config-gated APIs for acquiring, releasing, mapping, copying, page-size selection, and revocation.

Important APIs and types: `struct ib_umem` stores owning RDMA device, owning mm, IOVA, length, virtual address, DMA attrs, writable/ODP/dmabuf flags, and an appended scatter-gather table. `struct ib_umem_dmabuf` embeds `ib_umem` and tracks dma-buf attachment, sg table bounds/offset trim, revoke callback/private data, and pinned/revoked state. Inline helpers convert to dmabuf, compute page offset, first DMA address, DMA offset for a page size, number of DMA blocks/pages, best page size from offset bitmask, and contiguity. With `CONFIG_INFINIBAND_USER_MEM`, APIs include `ib_umem_get()`, `ib_umem_release()`, `ib_umem_copy_from()`, `ib_umem_find_best_pgsz()`, dma-buf get/pinned/revocable variants, map/unmap pages, release, revoke lock/unlock, and revoke. Without the config, stubs return `-EOPNOTSUPP`/0 or do nothing.

Control flow: uverbs/provider code pins or attaches user memory, builds DMA mappings in the SG table, selects hardware page size based on supported page-size bitmap and alignment, programs memory regions, and releases/unmaps on MR destruction. Dma-buf users may map lazily, pin, install revoke callbacks under revoke lock, and handle revocation by provider-specific teardown.

State and persistence: `ib_umem` is runtime registration state tying an mm/dma-buf to DMA mappings and an IOVA range. Pinned/revoked bits and SG tables are valid only while the registration exists. No file data is persisted by this layer.

Dependencies and integration points: depends on scatterlist/SG append tables, DMA mapping, pages, mm lifetime, dma-buf attachment APIs, RDMA device/provider MR setup, and config flags. It integrates uverbs memory registration, dma-buf sharing, and hardware page-size programming.

Risks and test signals: risks include page pin leaks, DMA unmap omissions, wrong IOVA/page-size math, overflow in block-count calculations, contiguity false positives, copying past umem bounds, dma-buf revoke races, config-stub signature drift, and writable flag mismatches. Test MR register/deregister under memory pressure, page-size selection matrices, offset/alignment edge cases, contiguous and fragmented SG tables, dma-buf pin/map/revoke/release, config-disabled builds, and lockdep around revoke locks.
