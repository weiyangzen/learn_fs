# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.c

## Purpose
This file provides scheduler policy helpers for i915 selftests. It can find an engine, temporarily modify scheduling/reset policy to accelerate hang/reset scenarios, restore saved policy, and wait for a request with a fixed reset-oriented timeout.

## Important APIs, Types, And Functions
- `intel_selftest_find_any_engine()` returns the first engine in a GT or logs absence.
- `intel_selftest_modify_policy()` saves reset/flags/timeslice/preempt settings and applies either fast-reset or no-hangcheck policy.
- `intel_selftest_restore_policy()` restores saved policy and updates GuC global policy where needed.
- `intel_selftest_wait_for_rq()` waits up to `WAIT_FOR_RESET_TIME_MS`.

## Control Flow
Modify first snapshots current engine/i915 settings into `intel_selftest_saved_policy`. For fast reset it enables reset mode `2`, forced preemption, and reduced timeslice/preempt timeout. For no hangcheck it sets preempt timeout to zero. If the engine uses GuC, it pushes policy changes via `intel_guc_global_policies_update()` and restores on update failure. Restore reverses the fields and also updates GuC policy.

## State And Persistence
The helper intentionally mutates global driver reset parameters, engine flags, and engine scheduling properties. The saved-policy struct is caller-owned and must be restored after the test. GuC policy updates persist until restored.

## Dependencies And Integration Points
It depends on GT/engine iteration, i915 params, scheduler property fields, GuC policy update APIs, and request wait. It is used by scheduler and hang/reset selftests that need shorter timeouts.

## Risks
Forgetting restore leaves the driver in altered reset/preemption mode. Invalid modify type returns `-EINVAL` after saving fields but before mutation. GuC update failures require rollback, which this helper attempts.

## Test Signals
Success is `0` from modify/restore and request wait. Request timeout or interrupted wait returns the underlying negative result.
