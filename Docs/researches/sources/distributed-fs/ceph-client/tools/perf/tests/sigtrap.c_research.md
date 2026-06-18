## sources/distributed-fs/ceph-client/tools/perf/tests/sigtrap.c

Purpose: C unit/integration test for synchronous `SIGTRAP` delivery from perf breakpoint events.
Important APIs/types/functions: `make_event_attr`, optional BTF helpers `attr_has_sigtrap` and `kernel_with_sleepable_spinlocks`, `sigtrap_handler`, `test_thread`, `run_test_threads`, `run_stress_test`, and `test__sigtrap`.
Control flow: installs a SA_SIGINFO SIGTRAP handler, opens a breakpoint event on `ctx.iterate_on` with `inherit_thread`, `remove_on_exec`, `sigtrap`, and `sig_data`, starts five threads, enables the event, and verifies each atomic access triggers a signal.
State and persistence: global `ctx` tracks expected TID signal debt, count, breakpoint target, and first siginfo; BTF handle is cached and freed.
Dependencies and integration: `sys_perf_event_open`, hw breakpoint support, pthreads, atomics, BTF when available, and `BP_SIGNAL_IS_SUPPORTED` from `tests.h`.
Risks: RT kernels with sleepable spinlocks may miss signals and are skipped; libc may lack exposed `si_perf_*` fields.
Test signals: exact signal count, zero remaining TID debt, expected `si_addr`, or skip for unsupported kernel/architecture.
