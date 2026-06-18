# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.c

## Purpose
This file provides a shared live-test cleanup gate. It waits for all GTs to become idle after a test and wedges a GT if it does not flush, preventing later tests from running on suspect hardware state.

## Important APIs, Types, And Functions
The single exported function is `igt_flush_test(struct drm_i915_private *i915)`.

## Control Flow
The helper iterates every GT and every engine in each GT. It records the maximum engine preempt timeout, checks whether the GT is already wedged, then waits for GT idle for about twice the longest preempt timeout. On timeout, it logs the caller address, dumps GEM trace data, wedges the GT, and returns `-EIO`.

## State And Persistence
It reads engine properties and GT wedge state. On failure it persistently marks the GT wedged for the current driver lifetime. It does not allocate or retain memory.

## Dependencies And Integration Points
It depends on `intel_gt_wait_for_idle()`, engine iteration, GT wedge APIs, and GEM tracing. It is used by live-test teardown, request cancellation, and other hardware selftests.

## Risks
The timeout is heuristic and tied to preemption properties. Too small a timeout causes false wedging; too large delays failure detection. Wedge state is intentionally severe and affects subsequent tests.

## Test Signals
Return `0` means all GTs idled. Return `-EIO` means existing wedge or idle timeout, with trace dump and caller symbol in logs.
