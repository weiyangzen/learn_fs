# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_odp.c

## Purpose

`rxe_odp.c` implements RXE on-demand paging for user memory regions, including ODP MR registration, MMU invalidation, page faulting, copy operations, atomics, atomic write, persistent flush, and `advise_mr` prefetch.

## Important APIs, Types, and Functions

Core functions include `rxe_odp_mr_init_user()`, `rxe_ib_invalidate_range()`, `rxe_odp_mr_copy()`, `rxe_odp_atomic_op()`, `rxe_odp_do_atomic_write()`, `rxe_odp_flush_pmem_iova()`, and `rxe_ib_advise_mr()`. Helpers map IOVA to ODP page indexes and fault ranges with `ib_umem_odp_map_dma_and_lock()`.

## Control Flow

ODP registration obtains an `ib_umem_odp`, installs RXE MMU notifier ops, snapshots pages, and marks the MR valid. Runtime access maps the target range under `umem_mutex`, faults missing pages if allowed, maps pages with `kmap_local_page()`, performs copy/atomic/flush work, then unlocks. Prefetch can run synchronously or as best-effort work on `rxe_wq`.

## State and Persistence Behavior

State persists in `struct rxe_mr`, the `ib_umem_odp`, PFN list, notifier registration, MR access flags, and queued prefetch work references. MMU invalidations mutate the PFN list.

## Dependencies and Integration Points

The file depends on RDMA ODP core, HMM PFNs, MMU interval notifiers, persistent memory cache flush helpers, RXE MR validation, and responder state codes. It is called from MR registration and responder data/atomic paths.

## Risks and Edge Cases

Implicit ODP is rejected. Locking is subtle because successful ODP map calls return with `umem_mutex` held. Atomics require range and 8-byte alignment checks. Async prefetch failures are not reported to callers. Non-blockable invalidations return false.

## Test Signals

Test ODP MR registration, page faults during read/write traffic, invalidation during traffic, atomics and atomic write on ODP memory, misaligned atomic rejection, `advise_mr` modes, persistent flush, and ODP-disabled builds.
