<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/doorbell.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/doorbell.c

## Purpose
Manages userspace doorbell page pinning and sharing for mlx5 uverbs resources. Multiple CQs/QPs can map doorbell records from the same user page, and this file keeps one pinned UMEM and mm reference per `(mm, page-aligned virtual address)` with a reference count.

## Important APIs, Types, And Functions
- `struct mlx5_ib_user_db_page` stores list linkage, pinned one-page UMEM, page-aligned user virtual address, refcount, owning `mm_struct`, and is protected by the ucontext doorbell-page mutex.
- `mlx5_ib_db_map_user()` finds or pins a user doorbell page, computes the DMA address plus page offset, stores the page in `db->u.user_page`, and increments the page refcount.
- `mlx5_ib_db_unmap_user()` decrements the refcount and on last use removes the list entry, drops the mm reference, releases UMEM, and frees the page descriptor.

## Control Flow
Mapping locks `context->db_page_mutex`, scans `context->db_page_list` for a page matching both `current->mm` and `virt & PAGE_MASK`, and reuses it if found. Otherwise it allocates a page descriptor, pins one page with `ib_umem_get()`, grabs the current mm with `mmgrab()`, and links the descriptor into the context list. In both new and reused cases it computes `db->dma` from the first DMA SG entry plus the intra-page offset and increments `refcnt`. Unmapping takes the same mutex and frees the descriptor only when the decremented refcount reaches zero.

## State And Persistence
State is per-user-context, in-memory, and tied to RDMA object lifetimes. Each mapped doorbell page pins one user page, holds one mm reference, and remains on `context->db_page_list` while at least one mlx5 DB record references it. `struct mlx5_db` stores the DMA address and backpointer to the shared page descriptor.

## Dependencies And Integration Points
The file depends on RDMA UMEM pinning, Linux mm reference helpers, scatter-gather DMA addresses, and mlx5 IB ucontext fields. It is used by user CQ/QP/SRQ creation paths that need firmware doorbell-record DMA addresses and by their destroy paths for cleanup.

## Risks And Edge Cases
The matching key includes `current->mm`, so mapping/unmapping must occur in a context where the original user mm is meaningful. `mlx5_ib_db_unmap_user()` assumes `db->u.user_page` is valid and mapped exactly once for each unmap call. DMA address derivation assumes the one-page UMEM has a usable first SG entry. Refcount and list mutation depend entirely on `db_page_mutex`; missing the mutex in a caller would race page reuse or free.

## Test Signals
Tests should create multiple user resources sharing the same doorbell page, resources on different offsets in that page, resources from different processes with the same virtual address, and destruction in varying order. KASAN/refcount and mm/UMEM leak checks are important, as are fork/exec/process-exit scenarios around uverbs resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/doorbell.c -->
