# sources/distributed-fs/ceph-client/block/blk-rq-qos.c

## Purpose

`blk-rq-qos.c` implements the generic request-queue QoS framework used by writeback throttling, latency control, and cost models. It provides a linked chain of QoS policies, dispatches lifecycle callbacks to each policy, manages wait queues for throttling, scales queue depth, and safely adds/removes policies under queue freeze.

## Important APIs, Types, And Functions

Callback fanout functions include `__rq_qos_cleanup()`, `__rq_qos_done()`, `__rq_qos_issue()`, `__rq_qos_requeue()`, `__rq_qos_throttle()`, `__rq_qos_track()`, `__rq_qos_merge()`, `__rq_qos_done_bio()`, and `__rq_qos_queue_depth_changed()`. `rq_wait_inc_below()` atomically reserves an inflight slot below a limit. `rq_qos_wait()` is the common throttling wait primitive. Queue-depth scaling is handled by `rq_depth_calc_max_depth()`, `rq_depth_scale_up()`, and `rq_depth_scale_down()`. Policy lifetime is managed by `rq_qos_add()`, `rq_qos_del()`, and `rq_qos_exit()`.

## Control Flow

The block hot path uses inline wrappers from `blk-rq-qos.h`, which call these fanout functions only if QoS is enabled and the queue has a policy chain. Each fanout walks `rqos->next` and calls the corresponding operation when present. Throttling policies call `rq_qos_wait()`: it first tries to acquire an inflight token without sleeping if no waiters are present, otherwise installs an exclusive wait entry with a custom wake function that atomically claims a token before waking the task. The first waiter rechecks acquisition to guarantee progress when no inflight process exists.

Adding a policy requires `q->rq_qos_mutex` and freezes the blk-mq queue so no I/O is in flight while inserting at the head of the chain and setting `QUEUE_FLAG_QOS_ENABLED`. Duplicate IDs return `-EBUSY`. Deletion similarly freezes, unlinks the policy, clears the queue flag if the chain is empty, and unfreezes. `rq_qos_exit()` drains all policies under the mutex and invokes each policy's `exit()`.

## State And Persistence Behavior

QoS state is in memory on `request_queue::rq_qos`, `struct rq_qos`, `struct rq_wait`, and `struct rq_depth`. Wait state uses an atomic inflight counter plus wait queue. Queue depth scaling maintains `scale_step`, `scaled_max`, current queue depth, default depth, and derived max depth. No state is persisted across queue destruction.

## Dependencies And Integration Points

It depends on blk-mq queue freeze/unfreeze, request/bio lifecycle hooks, wait queues, atomics, and the policy implementations referenced by `enum rq_qos_id` (`RQ_QOS_WBT`, `RQ_QOS_LATENCY`, `RQ_QOS_COST`). It integrates with `blk_mq_submit_bio()`, request issue/completion/requeue paths, sysfs WBT settings, and queue-depth changes from `blk-settings.c`.

## Risks And Edge Cases

`rq_qos_wait()` has subtle wakeup ownership rules: the wake function claims the token, removes the wait entry, and relies on memory-ordering semantics of `finish_wait()` and `list_del_init_careful()` to avoid use-after-free or double-token ownership. Cleanup callbacks must undo an extra local token if a race grants two. Queue freeze during add/delete is required because policy lists are traversed in hot paths. Depth scaling must avoid underflow/overflow of `scale_step` and handle queue-depth-one devices specially.

## Test Signals

Signals include WBT/latency throttling tests under concurrent bios, wakeup fairness with many waiters, add/delete policy operations under I/O, queue-depth change notifications, lockdep for `rq_qos_mutex` plus freeze, and stress tests that verify no inflight counter leaks after interrupted races.
