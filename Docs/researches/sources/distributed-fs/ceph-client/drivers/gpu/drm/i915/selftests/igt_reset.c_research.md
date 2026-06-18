# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.c

## Purpose
This file provides reset-control helpers for selftests that need to serialize against or force GT reset paths.

## Important APIs, Types, And Functions
- `igt_global_reset_lock()` blocks reset backoff and per-engine reset bits, waiting for any existing reset users.
- `igt_global_reset_unlock()` clears engine reset bits and reset backoff, then wakes waiters.
- `igt_force_reset()` wedges and resets the GT, returning whether the GT recovered from wedged state.

## Control Flow
The lock helper sets `I915_RESET_BACKOFF`, then sets every `I915_RESET_ENGINE + id` bit, waiting where needed. Unlock clears every engine bit and wakes per-bit waiters plus the reset queue. Force reset calls `intel_gt_set_wedged()` followed by `intel_gt_reset()`.

## State And Persistence
It mutates `gt->reset.flags` and can change GT wedged/recovered state. These changes affect global reset behavior beyond the local helper call until unlocked or reset completes.

## Dependencies And Integration Points
It depends on GT reset flags, engine iteration, wait queues, and core GT reset APIs. Reset and hangcheck tests use it to coordinate reset-sensitive sections.

## Risks
Forgetting to unlock leaves reset bits set and can block reset progress. `igt_force_reset()` is invasive and should be used only where a reset is expected.

## Test Signals
Lock/unlock do not return status; force reset returns true only if the GT is no longer wedged after reset.
