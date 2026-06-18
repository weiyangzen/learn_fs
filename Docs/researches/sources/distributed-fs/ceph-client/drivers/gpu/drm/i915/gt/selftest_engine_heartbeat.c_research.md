# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.c

Purpose: tests and exposes helper controls for i915 engine heartbeat behavior, especially idle-barrier flushing, manual pulse behavior, and disabling heartbeat without leaving scheduled work behind.

Important APIs/functions: entry point `intel_heartbeat_live_selftests()` runs `live_idle_flush`, `live_idle_pulse`, and `live_heartbeat_off`. Exported test helpers are `st_engine_heartbeat_disable()`, `st_engine_heartbeat_enable()`, `st_engine_heartbeat_disable_no_pm()`, and `st_engine_heartbeat_enable_no_pm()`. Internal helpers include `reset_heartbeat()`, `timeline_sync()`, `engine_sync_barrier()`, `pulse_create()`, `pulse_unlock_wait()`, and `__live_idle_pulse()`.

Control flow: idle pulse tests create a temporary `pulse` object with `i915_active`, preallocate/acquire an idle barrier on an awake engine, call either `intel_engine_flush_barriers()` or `intel_engine_pulse()`, verify barrier tasks were consumed, synchronize via the kernel timeline, and confirm the active object retires. `live_heartbeat_off()` gets an engine wakeref, verifies heartbeat delayed work is running, calls `intel_engine_set_heartbeat(engine, 0)`, flushes delayed work, checks that work and systole state are gone, and restores the default interval.

State and persistence behavior: tests temporarily force hangcheck high, disable/re-enable heartbeat intervals, hold engine PM references, and use a refcounted `pulse` object whose `i915_active` callback retains the object until retirement. The no-PM disable helper parks heartbeat only if the engine is already awake to avoid making engines appear busy.

Dependencies and integration points: integrates with `intel_engine_heartbeat`, GT request synchronization, active barrier infrastructure, delayed work, heartbeat properties/defaults, PM wakerefs, and GT live selftest harness.

Risks: heartbeat interval changes must always be restored or later tests may run without heartbeat coverage. Idle-barrier assumptions depend on non-wedged engines and correct kernel context timeline progress. Tests that hold PM refs can affect idle detection if cleanup fails.

Test signals: failures print missing heartbeat pulse, unflushed idle tasks, heartbeat still running/allocated after disable, or timeout waiting for kernel timeline progress. The suite skips wedged GTs and ignores `-ENODEV` from pulse on unsupported engines.
