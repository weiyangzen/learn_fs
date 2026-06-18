<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_misc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_misc.c

## Purpose

Provides PVRDMA page-directory allocation/population/cleanup and conversion helpers between PVRDMA ABI types and RDMA core types.

## Important APIs, Types, And Functions

Page-directory APIs include `pvrdma_page_dir_init()`, `pvrdma_page_dir_cleanup()`, `pvrdma_page_dir_insert_dma()`, `pvrdma_page_dir_insert_umem()`, `pvrdma_page_dir_insert_page_list()`, and `pvrdma_page_dir_get_dma()`. Conversion helpers include QP cap, GID, global route, AH attr, and GID type conversions.

## Control Flow

`pvrdma_page_dir_init()` allocates one coherent directory page, coherent table pages, and optionally coherent data pages; optional pages are inserted into the tables as DMA addresses. User-backed objects call `pvrdma_page_dir_insert_umem()` to populate entries from pinned DMA blocks. Fast-reg MRs call `pvrdma_page_dir_insert_page_list()`.

Cleanup frees optional data pages, table pages, and the directory. Conversion functions copy or translate fields used by query/modify QP and AH handling.

## State And Persistence Behavior

Page directories persist in CQ, QP, SRQ, MR, and device ring objects. They hold DMA addresses visible to the backend. Conversion helpers are stateless.

## Dependencies And Integration Points

Depends on DMA coherent allocation, RDMA umem block iteration, PVRDMA device ABI page-directory macros, and RDMA AH/GID APIs.

## Risks And Edge Cases

`pvrdma_page_dir_init()` returns `-ENOMEM` for all cleanup paths, including oversized `npages` caught before allocation as `-EINVAL`. `npages == 0` would make `PVRDMA_PAGE_DIR_TABLE(npages - 1)` problematic, so callers must avoid zero-page directories unless audited. Umem insertion relies on caller-provided `npages` matching DMA block count.

## Test Signals

Test coherent page-directory creation with and without data pages, max-page rejection, umem insertion, cleanup after partial allocation failure, fast-reg page-list insertion bounds, and AH/GID route conversion round trips.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_misc.c -->
