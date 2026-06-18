# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_pm.c

Purpose: implements live selftests for engine timestamp correctness, busy-time accounting, and engine PM wakeref behavior under atomic contexts.

Important APIs/functions: public entry `live_engine_pm_selftests()` runs `live_engine_timestamps`, `live_engine_busy_stats`, and `live_engine_pm`. Helpers include `emit_wait()`, `emit_store()`, `emit_srm()`, `write_semaphore()`, `__measure_timestamps()`, `__live_engine_timestamps()`, `__spin_until_busier()`, and `trifilter()`.

Control flow: timestamp tests emit a request that signals a CPU semaphore, waits, stores ring and context timestamps before/after a controlled busy window, then compares GPU deltas with wall-clock time and with each other. Busy-stat tests measure near-zero busyness while idle, run an `igt_spinner` request to force 100% busy, optionally wait for GuC busyness propagation, and assert measured busy time is within tolerance. The PM test iterates `igt_atomic_phases`, takes a normal engine PM ref, then from atomic context tests `intel_engine_pm_get_if_awake()` and `intel_engine_pm_put_async()`, flushes PM, and checks the engine/GT return idle.

State and persistence behavior: uses engine status page slots as temporary semaphores/timestamp storage. Temporarily disables heartbeat around timestamp and busy-stat tests. Manipulates engine PM references and GT idle state, but should leave GT idle after each phase. The spinner is initialized once and ended after each engine.

Dependencies and integration points: depends on MI semaphore/store/SRM commands, timestamp registers, GT clock conversion helpers, GuC busy-time behavior, RPS/PM infrastructure, atomic selftest phases, spinner library, and heartbeat selftest helpers.

Risks: timing tolerances can be sensitive to virtualization, slow scheduling, or inaccurate `gt->clock_frequency`. Busy stats differ under GuC because accounting may update after workload start. CPU semaphore polling disables preemption/interrupts in tight windows, so tests should remain short. Cleanup must end spinners and re-enable heartbeat on errors.

Test signals: logs elapsed, CTX_TIMESTAMP, and RING_TIMESTAMP values; reports mismatch when deltas fall outside 25% tolerance. Busy-stat failures report idle busyness or busy percentage outside expected bounds. PM failures show failed `get_if_awake()`, engines still awake, or GT failing to idle.
