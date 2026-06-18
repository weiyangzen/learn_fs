<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_mr.c

## Purpose

Implements PVRDMA memory-region verbs: DMA MR creation, userspace MR registration, fast-reg MR allocation, deregistration, and scatterlist mapping for fast registration.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_get_dma_mr()`, `pvrdma_reg_user_mr()`, `pvrdma_alloc_mr()`, `pvrdma_dereg_mr()`, and `pvrdma_map_mr_sg()`. Helper `pvrdma_set_page()` appends pages to the fast-reg page list.

## Control Flow

DMA MR creation supports only `IB_ACCESS_LOCAL_WRITE`, posts `PVRDMA_CMD_CREATE_MR` with `PVRDMA_MR_FLAG_DMA`, and stores returned lkey/rkey/handle. User MR registration validates length, pins umem, builds a page directory from DMA blocks, posts create MR with start/length/access/nchunks/pdir, and stores returned keys. Fast-reg allocation creates an empty page list and page directory, creates an FRMR backend object, and later `pvrdma_map_mr_sg()` fills the page list through `ib_sg_to_pages()`.

Deregistration posts destroy MR, logs failures, then frees page directory, umem, fast-reg pages, and wrapper memory regardless of command result.

## State And Persistence Behavior

MRs hold backend handle, keys, IOVA/size, optional umem pins, page directories, and fast-reg page lists. Device backend state persists until destroy command or device teardown.

## Dependencies And Integration Points

Depends on RDMA MR APIs, umem, scatterlist-to-pages helper, PD handles from `pvrdma_verbs.c`, command posting, and page-directory helpers.

## Risks And Edge Cases

Destroy command failures do not prevent local resource release, which avoids leaks but can leave backend state until device reset. Fast-reg page-list length is capped at `PVRDMA_MAX_FAST_REG_PAGES`. User MR registration rejects zero length and lengths above backend max. `pvrdma_map_mr_sg()` records DMA addresses in `mr->pages`; correctness depends on later post-send fast-reg WQE inserting them into the page directory.

## Test Signals

Test unsupported DMA access flags, zero/too-large user MR, umem pin failure, page-directory allocation failure, create/destroy command failures, fast-reg max pages, scatterlist mapping offsets, and key propagation to userspace.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_mr.c -->
