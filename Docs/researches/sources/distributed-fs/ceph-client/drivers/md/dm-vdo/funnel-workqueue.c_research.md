# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.c

## Purpose
`funnel-workqueue.c` builds VDO kernel worker queues on top of funnel queues. It supports single-thread simple queues and multi-thread round-robin queues, completion priority selection, kthread lifecycle, idle wakeup optimization, debugging dumps, and current-workqueue introspection.

## Important APIs, Types, And Functions
- `struct vdo_work_queue` is the common external representation with name, owner thread, type, and mode.
- `struct simple_work_queue` owns priority funnel queues, private context, wait queue, idle flag, and worker kthread.
- `struct round_robin_work_queue` owns an array of simple service queues.
- Core processing: `poll_for_completion()`, `enqueue_work_queue_completion()`, `wait_for_next_completion()`, `process_completion()`, `service_work_queue()`, and `work_queue_runner()`.
- Lifecycle APIs: `vdo_make_work_queue()`, `vdo_finish_work_queue()`, `vdo_free_work_queue()`.
- Debug/introspection APIs: `vdo_dump_work_queue()`, `vdo_dump_completion_to_buffer()`, `vdo_get_current_work_queue()`, `vdo_get_work_queue_owner()`, `vdo_get_work_queue_private_data()`, and `vdo_work_queue_type_is()`.
- Submission API: `vdo_enqueue_work_queue()`.

## Control Flow And Data Flow
Creation either builds one simple queue or a round-robin wrapper with multiple simple queues. Each simple queue creates priority-specific funnel queues, starts a kthread, and waits until the worker has entered VDO code. The worker runs optional start hooks, repeatedly polls for completions from highest priority to lowest, sleeps when no work is visible, runs completions with `vdo_run_completion()`, and exits after `kthread_should_stop()` once pending work is drained.

Submission resolves a round-robin queue to one subordinate simple queue using a per-CPU rotor, sets a default priority if needed, marks `completion->my_queue`, puts the completion on the priority funnel queue, and uses the `idle` atomic flag plus barriers/CMPXCHG to avoid excessive wakeups while still waking a possibly sleeping worker.

## State And Persistence Behavior
All state is volatile worker scheduling state. Completion ownership is tracked through `completion->my_queue`; processing clears it before callback execution. Queue lifecycle is explicit: `vdo_finish_work_queue()` stops threads, and `vdo_free_work_queue()` then frees queues, names, and subordinate structures.

## Dependencies And Integration Points
The file depends on Linux kthread, waitqueue, completion, percpu, atomic, cache, and task-state APIs plus VDO `completion.h`, `funnel-queue.h`, logging, memory allocation, numeric, assertions, strings, and status codes. It is the generic executor for VDO completions across packer, logical-zone, bio, and other VDO thread domains.

## Risks
- Priority ordering is best-effort; a race can cause lower-priority work to be processed before newly visible high-priority work.
- No completions should be enqueued after `vdo_finish_work_queue()`; the code documents this as a caller contract.
- Wakeup minimization relies on subtle barriers around `idle` and funnel queue visibility.
- `get_current_thread_work_queue()` intentionally returns NULL in interrupt context to avoid nested completion processing assumptions.
- Round-robin distribution uses a per-CPU rotor shared across queues, so it is approximate rather than strict.

## Test Signals
Tests should cover single and multi-thread queues, start/finish hook invocation, priority fallback, invalid priority clamping, enqueue and stop races, current-queue introspection from worker and non-worker contexts, and dump formatting for NULL callbacks. Runtime signals are no stuck kthreads on teardown and no completion left with stale `my_queue`.
