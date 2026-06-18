<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.h

## Purpose
`intel_context.h` declares the core context API and defines inline helpers for context references, pinning, timeline locking, activity entry/exit, scheduling flags, ban/revoke state, and runtime clocks.

## Important APIs, Types, and Functions
The header exposes creation/lifecycle functions, pin/unpin functions, request helpers, remote request preparation, active request lookup, SSEU reconfiguration, and runtime statistic readers. Important inlines include `intel_context_is_child()`, `intel_context_is_parent()`, `intel_context_to_parent()`, `intel_context_is_parallel()`, `intel_context_lock_pinned()`, `intel_context_is_pinned()`, `intel_context_pin()`, `intel_context_pin_ww()`, `intel_context_unpin()`, `intel_context_enter()`, `intel_context_exit()`, `intel_context_get()`, `intel_context_put()`, `intel_context_timeline_lock()`, `intel_context_close()`, flag getters/setters for semaphores/banned/exiting/nopreempt/own-state, and `intel_context_clock()`.

## Control Flow
Most helpers are small state transitions. Pinning first tries to increment a nonzero `pin_count`, falling back to the full pin path. Unpin either directly decrements or hands the final pin to an asynchronous `sched_disable()` operation. Enter/exit update `active_count`, call backend `enter`/`exit`, and hold/release GT PM wakerefs while active. Timeline locking uses nested lock classes for parent and child parallel contexts.

## State and Persistence
The header manipulates persistent `struct intel_context` fields defined in `intel_context_types.h`: flags, pin count, active count, timeline, wakeref, ops, and parallel metadata. It also defines constants such as `PARENT_SCRATCH_SIZE` and `INTEL_CONTEXT_BANNED_PREEMPT_TIMEOUT_MS`.

## Dependencies and Integration Points
It depends on active tracking, driver types, engine types, ring/timeline types, GT PM, and trace helpers. It is included by nearly every GT component that creates requests, submits work, waits on contexts, or manages context power state.

## Risks and Edge Cases
Inline state changes are widely used and must preserve locking expectations. `intel_context_to_parent()` asserts parent pinning before child access. The asynchronous sched-disable unpin path can leave `pin_count == 2` while scheduling disable owns a pin. `intel_context_close()` does not itself wait for users; backend `close` behavior matters.

## Test Signals
Build coverage catches API drift. Runtime signals include lockdep for timeline nesting, pin/unpin balance, context active PM reference balance, nopreempt/banned/exiting flag semantics, and parallel submission selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.h -->
