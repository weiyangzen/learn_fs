# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_priolist_types.h

## Purpose

`i915_priolist_types.h` defines the request-priority constants and the scheduler priority-list node used by i915 request scheduling. It is small but important because it encodes special internal priorities above and below the user-visible context priority range.

## Important APIs, types, and functions

The exported constants are `I915_PRIORITY_MIN`, `I915_PRIORITY_NORMAL`, `I915_PRIORITY_MAX`, `I915_PRIORITY_HEARTBEAT`, `I915_PRIORITY_DISPLAY`, `I915_PRIORITY_INVALID`, `I915_PRIORITY_UNPREEMPTABLE`, and `I915_PRIORITY_BARRIER`. `struct i915_priolist` contains a `requests` list, an RB-tree `node`, and the integer `priority`.

## Control flow

There is no executable control flow. Scheduler code inserts priolist nodes into RB trees by priority and keeps requests with the same priority on the embedded list. Special priorities influence preemption and barrier behavior when the scheduler chooses runnable requests.

## State and persistence behavior

The priolist nodes are in-memory scheduler state. They persist while requests are queued at a priority level and are freed when no longer needed. `I915_PRIORITY_UNPREEMPTABLE` is specifically used for performance-query requests that must not be preempted once active, which ties this header to the OA/perf query safety model.

## Dependencies

The header depends on Linux list and rbtree types plus i915 uAPI priority constants from `i915_drm.h`. It is included by `i915_scheduler_types.h` and scheduler helpers.

## Integration points

Scheduler structures embed `struct i915_priolist`, and scheduler code uses the constants to order normal user requests, heartbeat pulses, display-critical work, barriers, and unpreemptable perf-query work. The perf-query comment documents why some requests need to remain active until completion.

## Risks

Changing numeric ordering can break preemption semantics, starve user workloads, or allow performance queries to be preempted in a way that corrupts measurements. `I915_PRIORITY_INVALID` relies on `INT_MIN`, and `I915_PRIORITY_UNPREEMPTABLE`/`BARRIER` rely on the top of the integer range, so arithmetic around priorities must avoid overflow.

## Test signals

Scheduler selftests, heartbeat tests, display pageflip latency tests, and OA/perf query tests that require unpreemptable execution are the main signals. Stress tests with mixed user priorities should verify no starvation or incorrect RB-tree ordering.
