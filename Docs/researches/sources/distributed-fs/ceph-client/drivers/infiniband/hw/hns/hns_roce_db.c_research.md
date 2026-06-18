# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_db.c

Purpose: Manages doorbell record memory for user and kernel consumers. Doorbell records are small DMA-visible words used by hardware to observe queue producer/consumer indexes.

Important APIs/types/functions: `hns_roce_db_map_user()` pins and maps a user page containing DB records. `hns_roce_db_unmap_user()` releases references. `hns_roce_alloc_db()` allocates a kernel DB record from coherent per-page pgdirs. `hns_roce_free_db()` returns it and frees empty pgdirs.

Control flow: User mapping serializes on the ucontext page mutex, reuses an existing pinned page for the same page-aligned virtual address or pins a new page with `ib_umem_get()`, then computes DMA and CPU virtual offsets. Kernel allocation searches existing pgdirs with a simple buddy-like bitmap for order 0 or order 1 records, allocating a new coherent page if needed. Free coalesces order-0 buddies into order 1 and releases pgdir pages when fully free.

State and persistence: User DB pages are cached in `hns_roce_ucontext.page_list` with refcounts. Kernel DB pages live in `hr_dev->pgdir_list`, protected by `pgdir_mutex`, and persist until all records are freed.

Dependencies and integration: Used by CQ/QP/SRQ creation paths. Depends on RDMA umem internals, scatterlist DMA addresses, coherent DMA, mutexes, bitmaps, and refcount helpers.

Risks: `hns_roce_db_map_user()` initializes refcount to one and increments again on first use; unmap decrements then conditionally decrements if one, which is a non-obvious lifetime pattern that deserves stress testing. User page assumptions depend on a single-page umem and valid SG mappings. Test signals include repeated DBs on one user page, concurrent ucontext map/unmap, kernel order-0/order-1 fragmentation, pgdir full/free transitions, and CQ/QP teardown leak checks.
