<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.c

## Purpose
`intel_context.c` implements the core i915 hardware context lifecycle: allocation, initialization, state allocation, pin/unpin, active tracking, request creation, parent/child binding for parallel submission, runtime statistics, and ban/revoke behavior.

## Important APIs, Types, and Functions
Public functions include `intel_context_create()`, `intel_context_alloc_state()`, `intel_context_free()`, `__intel_context_do_pin_ww()`, `__intel_context_do_pin()`, `__intel_context_do_unpin()`, `intel_context_init()`, `intel_context_fini()`, `i915_context_module_init()`, `i915_context_module_exit()`, `intel_context_enter_engine()`, `intel_context_exit_engine()`, `intel_context_prepare_remote_request()`, `intel_context_create_request()`, `intel_context_get_active_request()`, `intel_context_bind_parent_child()`, `intel_context_get_total_runtime_ns()`, `intel_context_get_avg_runtime_ns()`, `intel_context_ban()`, and `intel_context_revoke()`.

## Control Flow
Creation allocates from a slab and initializes fields from the engine. State allocation runs under `pin_mutex`, rejects banned contexts, calls `ce->ops->alloc()`, sets `CONTEXT_ALLOC_BIT`, and accounts objects to DRM clients. Pinning ensures state is allocated, locks HWSP/ring/state objects through the ww context, pins ring/timeline/state, calls backend `pre_pin`, acquires active tracking, serializes on `pin_mutex`, rejects closed contexts, performs first-pin backend setup, and publishes `pin_count`. Unpin decrements `pin_count`, calls backend unpin/post-unpin at zero, releases active tracking, and preserves a temporary context reference across asynchronous active release. Request creation pins the context, creates an i915 request, unpins, and adjusts lockdep nesting for timeline mutex use.

## State and Persistence
Persistent state includes the context reference, VM reference, timeline, ring, state VMA, `pin_count`, `active_count`, `i915_active`, flags, GuC state, parallel relationship fields, runtime EWMA/total counters, and slab allocation. Pinned state prevents shrinker reclamation of ring/context/timeline objects while GPU-visible. RCU delayed free protects readers of context fields.

## Dependencies and Integration Points
The file depends on GEM object/VMA locking and pinning, timelines, rings, `i915_active`, request creation, scheduler/GuC state, DRM client accounting, tracepoints, and engine PM. It is used by engine setup, userspace context creation, kernel contexts, request submission, hang recovery, and context reconfiguration paths.

## Risks and Edge Cases
The pin path has multiple nested resources and must unwind in exact reverse order. `pin_count` publication uses memory barriers so other CPUs do not see a pinned context before backend state is valid. Closed/banned contexts reject new pin/allocation. Remote requests must not target their own context and must keep the target context image/timeline pinned until the modifying request retires. Parallel parent/child pointers rely on immutability after binding and parent pinning for safe child access.

## Test Signals
Signals include context creation/destruction stress, ww deadlock retry coverage, pin/unpin reference balance, shrinker interaction, request creation under memory pressure, banned/revoked context behavior, GuC active request lookup, runtime accounting, parallel context binding, and selftests included under `CONFIG_DRM_I915_SELFTEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.c -->
