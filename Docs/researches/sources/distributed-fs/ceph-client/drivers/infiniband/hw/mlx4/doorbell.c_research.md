# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/doorbell.c

## Purpose
`doorbell.c` maps and unmaps userspace doorbell pages for mlx4 user objects.

## Important APIs, Types, And Functions
`struct mlx4_ib_user_db_page` tracks one pinned user page, its virtual page base, refcount, and list node. `mlx4_ib_db_map_user()` finds or pins the page containing a user doorbell address, computes the DMA address for the requested offset, stores the page pointer in `struct mlx4_db`, and increments the page refcount. `mlx4_ib_db_unmap_user()` decrements the refcount and releases the umem/page object when the last mapping is gone.

## Control Flow
Map obtains the ucontext from udata, locks `db_page_mutex`, searches `db_page_list` for `virt & PAGE_MASK`, allocates and pins a new page if missing, links it, computes `db->dma`, stores `db->u.user_page`, increments refcount, and unlocks. Unmap locks, decrements, removes/releases/frees on zero, and unlocks.

## State And Persistence
Pinned doorbell pages are cached per user context in `db_page_list`. Each `struct mlx4_db` references a cached page and DMA offset. State lasts until all CQ/QP/SRQ users of that doorbell page unmap it or the ucontext is destroyed.

## Dependencies And Integration Points
The file uses RDMA udata-to-ucontext helpers, `ib_umem_get()`/`ib_umem_release()`, SG DMA address extraction, and is used by mlx4 user CQ/QP/SRQ creation paths.

## Risks
DMA address uses the first SG entry plus offset, assuming a single pinned page layout. Refcounting depends on every successful map being paired with unmap. The page cache is protected by a mutex, but consumers must not access `db->u.user_page` after unmap.

## Test Signals
Test mapping two doorbells on the same page, mapping different pages, pin failure, allocation failure, exact DMA offset calculation, refcounted unmap, and concurrent map/unmap from one ucontext.
