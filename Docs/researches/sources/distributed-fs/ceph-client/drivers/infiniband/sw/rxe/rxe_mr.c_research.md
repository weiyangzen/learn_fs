# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mr.c

## Purpose
`rxe_mr.c` implements RXE memory region state, key generation, user memory pinning, fast registration, scatterlist mapping, MR copy, persistent-memory flush, atomic operations, DMA descriptor advancement, lookup/access validation, invalidation, and cleanup.

## Important APIs, types, and functions
Key functions include `rxe_get_next_key()`, `mr_check_range()`, `rxe_mr_init()`, `rxe_mr_init_dma()`, `rxe_mr_init_user()`, `rxe_mr_init_fast()`, `rxe_map_mr_sg()`, `rxe_mr_copy()`, `copy_data()`, `rxe_flush_pmem_iova()`, `rxe_mr_do_atomic_op()`, `rxe_mr_do_atomic_write()`, `advance_dma_data()`, `lookup_mr()`, `rxe_invalidate_mr()`, `rxe_reg_fast_mr()`, and `rxe_mr_cleanup()`. State includes `struct rxe_mr`, page-info arrays, `ib_umem`, access flags, keys, state enum, and `atomic_ops_lock`.

## Control flow
MR initialization assigns pool-index-based lkey/rkey values with random low key bytes and starts most MRs invalid until the specific type marks them valid/free. User MR registration pins umem pages, allocates page-info entries, validates persistent-memory access if requested, fills page mappings, and marks the MR valid. Fast MRs allocate page-info capacity and become FREE until a REG_MR WQE supplies iova/key/access and transitions them valid. Copy paths validate range and access, choose DMA, ODP, or page-info copy, and advance DMA descriptors across SGEs while holding/dropping MR references. Remote atomic paths validate state, range, and 8-byte alignment, then update mapped pages under a global spinlock.

## State and persistence
MRs persist in RXE object pools until deregistration. User pages are pinned through `ib_umem`; page-info arrays map IOVA to pages and offsets. Fast-registration state toggles between FREE and VALID. `num_mw` blocks invalidation while memory windows are bound. Persistent-memory flushes write back cache lines but do not otherwise persist metadata.

## Dependencies and integration points
The file integrates with RDMA umem, virtual DMA helpers, scatterlist-to-page mapping, ODP stubs/implementation, libnvdimm persistent-memory detection, RXE responder/requester/completer copy paths, MW binding, and pool reference management.

## Risks
Range arithmetic `iova + length` can overflow if not otherwise constrained. Page-size compatibility in fast registration is subtle, especially when MR page size is larger or smaller than PAGE_SIZE. Atomic operations use a global lock, which is simple but can bottleneck and must match memory ordering expectations. Invalidation must reject bound MRs and wrong key flavors. Persistent flush requires all pages to be pmem when access requests it.

## Test signals
Test user MR registration/deregistration, DMA MR access, fast-reg map sizes and page sizes, local and remote key lookup failures, copy across SGE/page boundaries, zero-length copy/flush, ODP enabled/disabled paths, persistent-memory access validation and flush, atomic compare-swap/fetch-add/write alignment errors, MW-bound invalidation rejection, and key rollover.
