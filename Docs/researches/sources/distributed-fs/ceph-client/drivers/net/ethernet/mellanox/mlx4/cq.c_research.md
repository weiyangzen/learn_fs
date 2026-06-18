# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cq.c

## Purpose
This file implements mlx4 core completion queue management: CQ number allocation, ICM mapping, firmware state transitions, CQ resize/moderation, completion/event dispatch, tasklet deferral, and CQ table lifecycle.

## Important APIs and Functions
- `mlx4_cq_alloc()` allocates a CQN, inserts the CQ into the radix tree, builds a CQ context mailbox, optionally initializes CQEs, and transitions the CQ from software to hardware ownership.
- `mlx4_cq_free()` transitions hardware back to software, removes the radix-tree entry, synchronizes IRQs, waits for refcount completion, and frees ICM.
- `mlx4_cq_completion()` and `mlx4_cq_event()` look up CQs by number and invoke completion or async event callbacks.
- `mlx4_cq_modify()` and `mlx4_cq_resize()` issue firmware modify commands.
- `mlx4_init_cq_table()` and `mlx4_cleanup_cq_table()` manage the CQ radix tree and bitmap.

## Control Flow
Completion events are normally dispatched by EQ code into `mlx4_cq_completion()`, which increments `arm_sn` and invokes the CQ completion callback. The default callback queues the CQ onto an EQ tasklet list with a refcount. The tasklet drains queued CQs for a bounded time and reschedules if work remains.

## State and Persistence
State includes the core CQ radix tree, bitmap of CQN ownership, ICM table references, per-CQ refcount/completion, arm sequence, EQ vector/IRQ, UAR, and tasklet list node. Hardware CQ state is persisted through firmware SW2HW/HW2SW/MODIFY commands.

## Dependencies and Integration Points
It depends on `mlx4_cmd*()` firmware commands, ICM tables, MTT addresses, EQ vectors, radix tree, RCU, IRQ synchronization, and CQ consumers such as mlx4_en and RDMA.

## Risks and Test Signals
Risks include use-after-free around interrupt dispatch, radix-tree stale entries, CQE initialization failures for user CQs, vector bounds mistakes, and multi-function resource mapping errors. Test signals include CQ create/destroy stress, interrupt affinity/vector tests, resize/moderation operations, user CQ creation, and IRQ synchronization under teardown.
