# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.c

## Purpose

`completion.c` implements VDO's lightweight asynchronous continuation primitive. A `vdo_completion` carries a callback, error handler, target thread, result, queue state, and parent pointer so multi-stage operations can move between VDO work queues without conventional locking between zones.

## Important APIs, Types, And Functions

- `vdo_initialize_completion`: clears a completion, assigns its owning VDO and type, then resets result/complete state.
- `vdo_set_completion_result`: records the first non-success result without masking an older error.
- `vdo_launch_completion_with_priority`: runs immediately if already on the target thread and not forced to requeue, otherwise enqueues to the target work queue.
- `vdo_finish_completion`: marks a completion complete and launches its callback if present.
- `vdo_enqueue_completion`: validates the target thread, clears `requeue`, sets priority, and enqueues on the VDO work queue.
- `vdo_requeue_completion_if_needed`: helper for callbacks that must resume on a specific thread.

## Control Flow

Operations prepare a completion with the next callback, error handler, target thread, and parent. Launching compares the target callback thread to `vdo_get_callback_thread_id`; matching-thread callbacks run inline unless `requeue` is set. Mismatched callbacks are queued. When a completion is run, `completion.h` dispatches to the error handler if `result` is not `VDO_SUCCESS` and an error handler exists; otherwise it calls the normal callback.

`vdo_finish_completion` is used when an asynchronous child operation is complete and should notify its parent callback. `complete` is a programming-error detector, not a cross-thread completion status.

## State And Persistence Behavior

This file does not persist data. It mutates in-memory completion fields: result, complete flag, requeue flag, priority, queue link metadata, callback thread id, callback, error handler, and parent. Result handling is sticky: after the first error, later success or errors do not overwrite it.

## Dependencies And Integration Points

The implementation depends on VDO thread configuration, `vdo_enqueue_work_queue`, callback-thread identity, `status-codes.h`, and assert/log helpers. It is the common substrate for `data_vio`, block-map cache I/O, VIO metadata/data I/O, admin actions, and pool release processing.

## Risks And Edge Cases

- Callers may not inspect or mutate most completion fields from arbitrary threads; ownership follows the currently executing callback thread.
- Calling `vdo_set_completion_result` or `vdo_finish_completion` on an already complete completion is a programming error.
- A null callback with `vdo_run_completion` would crash; callers must only launch runnable completions or finish completions with callback checks.
- `vdo_enqueue_completion` calls `BUG()` after an invalid thread assertion, so corrupted callback thread IDs are fatal.
- `requeue` is cleared on enqueue, so callers that need repeated forced queuing must set it before each launch.

## Test Signals

Tests should cover first-error-wins result behavior, immediate execution on the correct thread, queued execution on a different thread, forced requeue, invalid thread assertions, finish-without-callback behavior, and error-handler dispatch. Runtime failures often appear as completion type assertions, invalid thread BUGs, stack growth from missing requeue, or lost parent callbacks.
