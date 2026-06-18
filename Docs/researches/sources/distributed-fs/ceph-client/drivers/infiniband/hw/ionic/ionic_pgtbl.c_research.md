# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_pgtbl.c

Purpose: page-table buffer construction for Ionic RDMA objects. It converts either a single DMA address or an RDMA user memory object into the firmware page-table form used by MR, CQ, and QP creation and fast registration.

Important APIs/functions: `ionic_pgtbl_init()` initializes a `struct ionic_tbl_buf`; `ionic_pgtbl_page()` appends a DMA page; `ionic_pgtbl_dma()` returns either the page-table DMA address or direct DMA address plus VA offset; `ionic_pgtbl_off()` returns the offset for multi-page tables; `ionic_pgtbl_unbuf()` unmaps/frees the table buffer.

Control flow: initialization zeros the buffer, derives page count and page-size log from `ib_umem` when present, validates `limit`, allocates and DMA-maps an array of little-endian DMA entries only when more than one page is needed, then fills entries from `rdma_umem_for_each_dma_block()` or a single DMA address. Error paths unmap and clear the buffer.

State and persistence: `struct ionic_tbl_buf` records page count, limit, size, table virtual address, table DMA address, and page-size log. A one-page/direct mapping uses `tbl_dma` without allocating `tbl_buf`; multi-page mappings allocate a DMA-mapped table until `ionic_pgtbl_unbuf()`.

Dependencies and integration: uses RDMA umem block iterators, Linux DMA mapping, and Ionic firmware command fields that expect table DMA, map count, page-size log, and offsets. MR registration and queue creation consume this structure.

Risks: `order_base_2(page_size)` assumes valid power-of-two page sizes selected by callers. Single-page direct mode and multi-page table mode share `tbl_dma`, so callers must use `ionic_pgtbl_dma()`/`ionic_pgtbl_off()` rather than interpreting fields directly. `ionic_pgtbl_page()` enforces the limit but does not validate DMA alignment.

Test signals: user MR registration with one page and many pages, CQ/QP user queue mapping, fast-reg MR after `ib_map_mr_sg`, DMA mapping failure unwinds, and page sizes across supported 4K/2M/1G capabilities.
