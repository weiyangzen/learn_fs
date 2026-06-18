<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_ratelimit.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_ratelimit.c

## Purpose
KUnit tests for `___ratelimit()` behavior, covering basic burst/interval semantics, disabled/unlimited modes, re-enabling, and concurrent stress accounting.

## APIs, Types, and Functions
Uses `DEFINE_RATELIMIT_STATE()`, `RATELIMIT_STATE_INIT_FLAGS()`, `___ratelimit()`, `ratelimit_state_reset_miss()`, `kthread_run()`, `kthread_stop()`, `schedule_timeout_idle()`, and CPU mask helpers. `struct stress_kthread` records attempts, allowed calls, limited calls, missed counts, and task pointer.

## Control Flow, State, and Persistence
`test_ratelimit_smoke()` consumes a three-event burst, sleeps partial and full intervals, mutates `testrl.burst` and `testrl.interval`, and checks boolean decisions. `test_ratelimit_stress()` spawns one low-priority worker per online CPU for two seconds; each worker loops on `___ratelimit()`, counts results, and reads missed counts on exit. The final aggregate asserts allowed+limited equals attempts and limited equals missed. Static ratelimit state and `doneflag` persist across the module lifetime.

## Dependencies and Integration
Depends on KUnit, ratelimit internals, scheduler sleeps, kthreads, CPU masks, and memory allocation. Both test cases are marked `KUNIT_CASE_SLOW`.

## Risks and Test Signals
Risks include wall-clock duration, scheduler timing sensitivity, `doneflag` not reset if the stress test were rerun in the same module instance, high CPU-count fanout, and missed cleanup if thread creation partially fails. Test signals include interval boundary behavior, burst-zero disable semantics, interval-zero unlimited semantics, and concurrent accounting consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_ratelimit.c -->
