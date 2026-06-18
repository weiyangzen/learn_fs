# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cq.c

## Purpose

`cq.c` manages mlx5 completion queues at the core layer. It creates and destroys firmware CQs, registers them with completion and async EQ lookup trees, handles deferred completion callback processing via tasklets, and exposes query/modify helpers.

## Important APIs, Types, And Functions

- `mlx5_cq_tasklet_cb()`: drains a tasklet process list for a bounded time and invokes CQ completion callbacks.
- `mlx5_add_cq_to_tasklet()`: queues a CQ for tasklet processing while holding a CQ reference.
- `mlx5_create_cq()` / `mlx5_core_create_cq()`: create a firmware CQ, initialize software CQ state, register with EQs, and add debugfs state.
- `mlx5_core_destroy_cq()`: remove debug/EQ registrations, destroy the firmware CQ, synchronize IRQs, drop the final CQ reference, and wait for free completion.
- `mlx5_core_query_cq()`, `mlx5_core_modify_cq()`, and `mlx5_core_modify_cq_moderation()`: firmware query/modify helpers.
- `mlx5_core_cq_dummy_cb()`: default completion callback that logs if callers did not install one.

## Control Flow

Tasklet scheduling avoids duplicate list entries by checking `list_empty_careful()` under the tasklet context lock. The first queued CQ schedules the tasklet. The tasklet splices pending CQs into a process list, invokes each CQ's completion callback, drops the reference acquired during queueing, and reschedules itself if it exceeds the short time budget.

CQ creation obtains the target completion EQ from the command input, sends `CREATE_CQ` through `mlx5_cmd_do()`, initializes CQN, indices, arm sequence, EQ pointer, UID, optional arm doorbell, refcount, completion, callback, and tasklet context, then registers the CQ in both the completion EQ and async EQ trees. If async registration fails it unregisters from the completion EQ and destroys the firmware CQ.

Destroy removes debugfs and both EQ registrations before issuing `DESTROY_CQ`. On success it synchronizes the EQ IRQ, drops the CQ reference, and waits for outstanding tasklet/event users to finish.

## State And Persistence Behavior

CQ software state is held in caller-owned `struct mlx5_core_cq`: CQN, indices, arm state, EQ pointer, UID, refcount, completion, tasklet list node, callback, creator PID, and IRQ number. Firmware owns the actual CQ until destroy. There is no persistence across driver/device teardown.

## Dependencies And Integration Points

The file uses mlx5 command execution, EQ core registration (`mlx5_eq_add_cq()`, `mlx5_eq_del_cq()`), async EQ lookup, debug CQ tracking, Linux tasklets, IRQ synchronization, refcounts, and RDMA/core CQ structures. Upper layers such as netdev and RDMA create CQs through these exported helpers.

## Risks

- Destroy must account for tasklet-held references and late IRQs; removing EQ entries and synchronizing IRQ before waiting is important.
- `mlx5_create_cq()` uses `mlx5_cmd_do()` and leaves outbox status checking to callers on error; `mlx5_core_create_cq()` normalizes with `mlx5_cmd_check()`.
- Tasklet callback time slicing can defer completion handling under heavy CQ load.
- Callers must set `arm_db` for kernel CQs before creation when they expect command sequence initialization.

## Test Signals

Test CQ create/destroy success and failure at each registration step, completion event delivery through tasklet, duplicate queue suppression, destroy while tasklet work is pending, query/modify/moderation commands, and IRQ synchronization under stress. Debugfs CQ entries and refcount completion are useful leak signals.
