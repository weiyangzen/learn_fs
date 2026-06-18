<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.c

## Purpose
`intel_engine_pm.c` implements engine wakeref get/put callbacks. It resets/scrubs pinned contexts on unpark, starts breadcrumbs and heartbeats, parks engines by switching to a safe kernel context when needed, drains idle barriers, and initializes engine PM state.

## Important APIs, Types, and Functions
Public functions are `intel_engine_init__pm()` and `intel_engine_reset_pinned_contexts()`. Important internals include `intel_gsc_idle_msg_enable()`, `dbg_poison_ce()`, `__engine_unpark()`, `duration()`, `__queue_and_release_pm()`, `switch_to_kernel_context()`, `call_idle_barriers()`, and `__engine_park()`. `wf_ops` connects these callbacks to `intel_wakeref`.

## Control Flow
On unpark, the engine obtains a GT PM wakeref, waits for the kernel context to leave inflight state, optionally poisons the context image in debug builds, resets the kernel context image, calls backend unpark, unparks breadcrumbs, and starts heartbeat. On park, it clears saturation, attempts to switch to the perma-pinned kernel context for execlists-style safe suspend, returning `-EBUSY` if that request must first run. Once safe, it calls idle barrier callbacks, parks heartbeat and breadcrumbs, calls backend park, and asynchronously releases the GT wakeref. `switch_to_kernel_context()` constructs a barrier-priority request without the usual timeline mutex assumptions because engine PM park has exclusive submission ownership.

## State and Persistence
Persistent state includes `engine->wakeref`, `engine->wakeref_track`, `engine->wakeref_serial`, kernel context state, pinned context list, heartbeat/breadcrumb activity, and barrier task llist. Debug poisoning writes `CONTEXT_REDZONE` into context images to catch stale trust in suspend-corrupted state.

## Dependencies and Integration Points
The file depends on breadcrumbs, contexts, heartbeat, GT PM, RC6/GSC registers, ring/request internals, shmem utilities, and engine backend park/unpark/reset hooks. It is called from engine initialization and runtime PM wakeref transitions.

## Risks and Edge Cases
The park path is lock-order sensitive because it can run while retiring requests. It open-codes part of context enter and carefully orders timeline active-list insertion, request queueing, and wakeref deferred park to avoid underflow. GuC submission skips kernel-context switching because scheduling disable provides the idle guarantee. Pinned LMEM context images may be corrupted across suspend and must be reset.

## Test Signals
Signals include engine PM selftests, runtime suspend/resume with active and idle engines, kernel context switch-on-park, barrier callback flushing, breadcrumb/heartbeat active counts, GSC idle message setup on media v13, and pinned context reset after suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.c -->
