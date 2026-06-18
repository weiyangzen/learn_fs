# File Research: sources/block-storage/kvdo/vdo/completion.c

## Purpose

Implements VDO’s asynchronous completion primitive, including initialization, callback invocation, thread requeueing, error preservation, type assertions, and work-queue enqueueing.

## Main Responsibilities

- Maintains string names for completion types.
- Initializes and resets `struct vdo_completion`.
- Preserves first error result.
- Invokes callbacks immediately or enqueues them on the proper thread.
- Completes parent completions.
- Preserves child errors in parents while continuing processing.
- Asserts completion type.
- Enqueues completions into VDO thread work queues with priority.

## Important Functions

- `vdo_initialize_completion()` zeroes a completion, assigns VDO/type, and resets result state.
- `vdo_reset_completion()` resets result and complete flag.
- `vdo_set_completion_result()` records the first non-success result.
- `vdo_invoke_completion_callback_with_priority()` runs callback immediately if on target thread and not forced to requeue; otherwise enqueues.
- `vdo_continue_completion()` sets result and invokes callback.
- `vdo_complete_completion()` marks complete and invokes callback if set.
- `vdo_finish_completion_parent_callback()` finishes a parent completion.
- `vdo_preserve_completion_error_and_continue()` propagates error to parent, resets child, and continues.
- `vdo_assert_completion_type()` validates type and reports readable names.
- `vdo_enqueue_completion_with_priority()` places completion on the configured VDO work queue.

## Behavior Details

Completion results are sticky: once a non-success result is stored, later results do not mask it.

Thread affinity is enforced by `callback_thread_id`. If a completion is already on the right thread and `requeue` is false, callbacks run directly. Otherwise, completion is queued to the target VDO thread.

## Dependencies and Interactions

- Uses VDO thread configuration and work queues.
- Used throughout kvdo for admin operations, action managers, VIOs, page cache, block map, allocator, recovery, and flush flows.

## Notable Edge Cases

- Invalid target thread IDs trigger assertion and `BUG()`.
- Unknown completion type names are formatted into a static numeric buffer.
- `vdo_complete_completion()` asserts the completion was not already complete.
