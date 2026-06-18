# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/srq.c

## Purpose

`srq.c` manages mlx4 shared receive queues. It allocates SRQ ICM/table entries, creates hardware SRQ contexts, tracks live SRQs in a radix tree for event dispatch, arms and queries SRQs, and releases SRQ resources safely while asynchronous events may still hold references.

## Important APIs, Types, And Functions

- `mlx4_srq_alloc()` creates an SRQ, inserts it into the radix tree, builds the firmware SRQ context, and transitions it with `SW2HW_SRQ`.
- `mlx4_srq_free()` transitions the SRQ back to software, removes it from the radix tree, waits for outstanding event references, and frees ICM.
- `mlx4_srq_event()` looks up an SRQ from an async event and invokes its callback if it can acquire a refcount.
- `mlx4_srq_arm()` and `mlx4_srq_query()` wrap firmware arm/query commands.
- `__mlx4_srq_alloc_icm()` / `__mlx4_srq_free_icm()` are native table/bitmap allocation helpers.
- `mlx4_srq_alloc_icm()` / `mlx4_srq_free_icm()` use `ALLOC_RES`/`FREE_RES` when running in multi-function mode.
- `mlx4_init_srq_table()`, `mlx4_cleanup_srq_table()`, and `mlx4_srq_lookup()` manage the table/radix-tree container.

## Control Flow

Allocation reserves an SRQ number and ICM, inserts the caller-provided `struct mlx4_srq` into `srq_table->tree`, allocates a command mailbox, fills `struct mlx4_srq_context` with size, stride, XRC domain, CQ number, MTT base address, PD, and doorbell record address, then sends `SW2HW_SRQ`. On failure it removes the radix entry and frees ICM.

Freeing sends `HW2SW_SRQ`, logs but continues on command failure, deletes the radix-tree entry, drops the initial refcount, waits for event handlers to drain through the completion, and frees ICM.

Event dispatch masks the SRQN by `num_srqs - 1`, looks up the SRQ under the table spinlock, uses `refcount_inc_not_zero()` to avoid racing a free, invokes the event callback outside the lock, and completes the free path when the last reference drops.

## State And Persistence Behavior

Runtime state lives in `mlx4_priv(dev)->srq_table`: spinlock, radix tree, and bitmap for non-slave devices. Each `struct mlx4_srq` has `srqn`, callback, completion, and refcount state supplied by upper layers. Hardware SRQ context persists only in device firmware while the SRQ is active.

## Dependencies And Integration Points

The file integrates with mlx4 command wrappers, ICM table management, bitmap allocation, radix trees, MTT address helpers, and exported SRQ APIs used by RDMA/core consumers. In SR-IOV/multifunction mode, it delegates SRQ number and ICM allocation to the master resource tracker via wrapped `ALLOC_RES` commands.

## Risks

- Free continues after `HW2SW_SRQ` failure; this prevents software leaks but can leave firmware state uncertain.
- Radix-tree lookup masks SRQN with `num_srqs - 1`, relying on power-of-two sizing semantics from the device caps.
- Event callback correctness depends on upper layers not freeing callback-owned memory before `mlx4_srq_free()` completion.
- Allocation cleanup must keep radix, ICM table, completion table, and bitmap rollback in sync.

## Test Signals

Exercise SRQ allocate/free, forced failures after radix insertion and after mailbox allocation, async event delivery during free, query/arm command failures, and multifunction `ALLOC_RES`/`FREE_RES` delegation. KASAN/refcount debugging is useful for event/free races.
