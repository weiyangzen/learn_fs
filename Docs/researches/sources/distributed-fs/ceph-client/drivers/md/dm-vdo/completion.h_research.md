# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.h

## Purpose

`completion.h` declares and inlines the common VDO completion API. It provides small helpers for running, resetting, preparing, launching, failing, and type-checking asynchronous continuations.

## Important APIs, Types, And Functions

- `vdo_run_completion`: dispatches to `error_handler` for non-success results, otherwise to `callback`.
- `vdo_reset_completion`: clears result and complete state while preserving type, VDO, and parent-related fields.
- `vdo_launch_completion`, `vdo_launch_completion_with_priority`, and `vdo_enqueue_completion`: scheduling entry points.
- `vdo_continue_completion` and `vdo_fail_completion`: result-setting continuation helpers.
- `vdo_assert_completion_type`: runtime type check for container casts.
- `vdo_set_completion_callback`, `vdo_launch_completion_callback`, `vdo_prepare_completion`, and `vdo_prepare_completion_for_requeue`: callback setup helpers.
- `vdo_requeue_completion_if_needed`: thread-affinity helper.

## Control Flow

Most users call `vdo_prepare_completion` to reset and bind the next stage, then `vdo_launch_completion`. If the current stage obtained a result code, it uses `vdo_continue_completion`; fatal paths use `vdo_fail_completion`. Inline launch helpers are thin wrappers around the out-of-line scheduler in `completion.c`.

## State And Persistence Behavior

The header defines no durable state. It controls how a `struct vdo_completion` is reused between stages. Reset intentionally does not clear callback, error handler, parent, or target thread; prepare does reset those relevant fields for a new stage.

## Dependencies And Integration Points

The header depends on VDO status codes, types, and assertion helpers. It is included across the VDO subsystem wherever objects embed `struct vdo_completion`, including data VIOs, metadata VIOs, page completions, pool completions, and admin completions.

## Risks And Edge Cases

- `vdo_run_completion` assumes `callback` is non-null when no error handler is selected.
- `vdo_assert_completion_type` returns an error code, but many container helpers use it only for logging/assertion before continuing.
- `vdo_prepare_completion_for_requeue` forces one queued hop only because enqueue clears `requeue`.
- Reusing a completion without `vdo_reset_completion` can retain stale error state.

## Test Signals

Compile coverage should catch prototype drift with `completion.c`. Unit-style tests should verify reset/prepare field effects, callback versus error-handler selection, type assertion behavior, launch callback convenience helpers, and no stale result after reuse.
