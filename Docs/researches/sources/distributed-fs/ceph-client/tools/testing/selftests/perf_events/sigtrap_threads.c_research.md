# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/sigtrap_threads.c

Purpose: validates synchronous perf SIGTRAP delivery for inherited breakpoint events across threads, including enable, modify, stress, and enable/disable racing behavior.

Important APIs/types/functions: global `ctx` tracks desired thread signal sum, signal count, watched variable, and first `siginfo_t`. `make_event_attr()` creates a `PERF_TYPE_BREAKPOINT` event on `ctx.iterate_on` with `inherit_thread`, `remove_on_exec`, `sigtrap`, and `sig_data`. `sigtrap_handler()` verifies `TRAP_PERF`, records first siginfo, and subtracts the current tid from `tids_want_signal`. `test_thread()` coordinates through a barrier and repeatedly reads/writes the watched variable.

Control flow: fixture installs SIGTRAP handler, opens disabled perf event, and starts five threads blocked on a barrier. `remain_disabled` expects no signals. `enable_event` enables and expects one signal per thread plus one in parent. `modify_and_enable_event` changes attributes and validates new `sig_data`. `signal_stress` expects `NUM_THREADS * 3000` signals. `signal_stress_with_disable` toggles enable/disable until enough signals arrive.

State and persistence: process-local threads, atomic counters, signal handler, and perf fd. No filesystem state.

Dependencies/integration: requires hardware breakpoint perf support usable by the current user, pthreads, and kernel siginfo fields for perf.

Risks: timing-sensitive under heavy load; stress counts require reliable synchronous breakpoint delivery. Tests may hang if signals stop arriving after successful setup.

Test signals: kselftest assertions check counts, `si_addr`, `si_perf_type`, and `si_perf_data`; failures indicate perf inheritance or signal metadata regressions.
