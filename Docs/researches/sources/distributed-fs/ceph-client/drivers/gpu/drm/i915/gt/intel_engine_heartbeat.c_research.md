<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.c

## Purpose
`intel_engine_heartbeat.c` implements periodic engine liveness checks. While an engine is awake, it submits low-priority kernel-context pulse requests, escalates priority if a heartbeat stalls, and triggers engine/GT error handling when progress cannot be restored.

## Important APIs, Types, and Functions
Public functions include `intel_engine_init_heartbeat()`, `intel_engine_unpark_heartbeat()`, `intel_engine_park_heartbeat()`, `intel_gt_unpark_heartbeats()`, `intel_gt_park_heartbeats()`, `intel_engine_set_heartbeat()`, `intel_engine_pulse()`, and `intel_engine_flush_barriers()`. Key internals include `next_heartbeat()`, `heartbeat_create()`, `idle_pulse()`, `heartbeat_commit()`, `show_heartbeat()`, `reset_engine()`, `heartbeat()`, `__intel_engine_pulse()`, and `set_heartbeat()`.

## Control Flow
Unpark schedules delayed heartbeat work when the interval is nonzero. The worker flushes submission, checks any previous systole request, obtains an engine PM wakeref if awake, skips wedged GTs, detects disabled schedulers, escalates a stuck heartbeat through normal, heartbeat, and barrier priorities if scheduling supports it, or calls reset handling. If no heartbeat is outstanding and the engine serial changed, it tries to lock the kernel timeline, creates a kernel request, attaches idle barriers, queues it, and schedules the next heartbeat. Setting heartbeat changes the interval under engine PM and kernel timeline lock and optionally sends a barrier pulse to recheck execution.

## State and Persistence
Persistent heartbeat state lives in `engine->heartbeat.work`, `engine->heartbeat.systole`, `engine->heartbeat.blocked`, `engine->props.heartbeat_interval_ms`, `engine->wakeref_serial`, and request `emitted_jiffies`/priority fields. Outstanding systole requests hold references until completed or parked.

## Dependencies and Integration Points
The file depends on kernel workqueues, engine PM, kernel contexts, request creation/commit/queue internals, scheduler priority updates, barrier task handling, GT reset/error capture, GuC hung-context discovery, and engine dump diagnostics. PM unpark/park paths start and stop heartbeats.

## Risks and Edge Cases
Too-short custom heartbeat intervals can preempt innocent work or downgrade reset precision, so warnings are emitted when the interval is below twice preempt timeout. The worker must avoid blocking allocations and timeline locks in some paths. A stuck kernel timeline lock is itself treated as a possible liveness failure. GuC mode requires manual hung-context discovery if GuC hang detection is unavailable.

## Test Signals
Signals include heartbeat selftests, forced pulse behavior, priority escalation, disabled scheduler reset paths, hangcheck on/off behavior, engine park/unpark cancellation, barrier flush requests, and custom interval warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.c -->
