# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace-tcp.c

Purpose: this file implements TCP-AO-specific ftrace event matching for the selftest library. It lets tests register expected TCP hash/AO tracepoints and reports unexpected or missing events at tracer destruction.

Important APIs and types: `trace_event_names` maps `enum trace_events` to tracepoint names. `struct expected_trace_point` stores required event type, family, source/destination addresses, optional ports, L3 index, TCP flags, key IDs, MAC length, SNE, and match count. Public entry points are `__trace_event_expect` and `setup_aolib_ftracer`.

Control flow: tests add expectations through wrappers in `aolib.h`, which call `__trace_event_expect`. The ftrace line processor identifies event type with `check_event_type`, parses fields in `tracer_scan_event`, validates namespace cookie filtering, and calls `lookup_expected_event`. Expected lines are discarded; unexpected or unparsable lines are preserved. On destruction, `check_free_events` prints match stats and xfails unexpected trace lines.

State and persistence: expected tracepoints are held in a reallocating global array protected by `exp_tps_mutex`. Match counts accumulate during the run. `free_expected_events` releases the array from the tracer destructor. No trace output is persisted beyond test logs.

Dependencies and integration points: depends on `ftrace.c` for tracefs mounting, instance management, and tracer threads. It also depends on namespace cookies from `test_init_ftrace`, TCP tracepoint text formats, and `kernel_config_has(KCONFIG_FTRACE)`.

Risks: parser formats are tightly coupled to kernel tracepoint string layouts. `free_expected_events` sets `exp_tps = NULL` before `free(exp_tps)`, effectively leaking the old allocation; as test process lifetime is short, impact is limited but visible in code review. Missing ftrace support turns expectations into skips/no-ops.

Test signals: successful tracing reports either matched expectation counts or no unexpected trace events. Unexpected trace lines produce `test_xfail`, while expected-but-unseen events produce `test_fail`.
