# sources/distributed-fs/ceph-client/drivers/infiniband/core/mr_pool.c

## Purpose
`mr_pool.c` provides small exported helpers for maintaining a QP-associated pool of preallocated memory registrations. It lets upper-layer protocols avoid repeated MR allocation on hot I/O paths by taking and returning `struct ib_mr` objects from a caller-owned list.

## Important APIs, types, and functions
- `ib_mr_pool_get()` removes the first MR from a list under `qp->mr_lock`, increments `qp->mrs_used`, and returns `NULL` if the list is empty.
- `ib_mr_pool_put()` returns an MR to a list under the same lock and decrements `qp->mrs_used`.
- `ib_mr_pool_init()` allocates `nr` MRs using `ib_alloc_mr()` or `ib_alloc_mr_integrity()` depending on `enum ib_mr_type`, then appends them to the pool list.
- `ib_mr_pool_destroy()` removes all MRs from the list and deregisters them with `ib_dereg_mr()`.

## Control flow
Initialization loops until the requested pool size is reached. On allocation failure it destroys any MRs already added and returns the allocation error. Get/put are constant-time list operations. Destroy holds `qp->mr_lock` only while removing each list entry, releases it around `ib_dereg_mr()`, then reacquires it for the next entry.

## State and persistence
The pool is a caller-supplied `struct list_head` whose entries are linked through `ib_mr::qp_entry`. `qp->mrs_used` tracks checked-out MRs. There is no durable state; all MRs are RDMA core objects tied to the QP's PD and must be deregistered before teardown.

## Dependencies and integration points
The helpers use RDMA verbs allocation and deregistration APIs plus the QP's `mr_lock`. They export symbols for RDMA ULPs and drivers that maintain per-QP MR pools.

## Risks
- Callers must not destroy a pool while MRs are checked out; this helper only destroys entries currently on the list.
- The list must contain only MRs that belong to the same QP/PD context expected by the caller.
- `qp->mrs_used` can underflow or become inaccurate if callers put the same MR twice or mix lists.
- Because `ib_dereg_mr()` runs outside the spinlock, concurrent get/put during destroy must be prevented by higher-level teardown ordering.

## Test signals
- Unit or fault-injection tests should cover partial allocation failure and verify that already allocated MRs are deregistered.
- Concurrency tests should exercise get/put from multiple CPUs and verify `mrs_used` returns to zero.
- Integrity MR paths should be built and tested separately from regular MR allocation.
