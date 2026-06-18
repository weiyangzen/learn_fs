# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_heartbeat.h

Purpose: declares heartbeat control helpers shared by i915 live selftests that need to suppress or restore heartbeat behavior around timing-sensitive scenarios.

Important APIs/types: forward-declares `struct intel_engine_cs` and declares `st_engine_heartbeat_disable()`, `st_engine_heartbeat_disable_no_pm()`, `st_engine_heartbeat_enable()`, and `st_engine_heartbeat_enable_no_pm()`.

Control flow: none in the header; implementations adjust heartbeat interval and optionally engine PM state.

State and persistence behavior: callers rely on these helpers to preserve and restore heartbeat behavior using engine defaults. The `_no_pm` variants are intended for tests that cannot take a PM reference just to disable heartbeat.

Dependencies and integration points: included by execlists, engine PM, and heartbeat selftests to coordinate heartbeat suppression during spinners, timeslicing, and reset scenarios.

Risks: callers must pair disable and enable variants correctly. Mixing PM and no-PM variants can leave wakeref accounting or heartbeat interval state inconsistent.

Test signals: compile coverage plus runtime evidence from all live selftests that use heartbeat suppression.
