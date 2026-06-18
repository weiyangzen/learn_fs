# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace.c

Purpose: this file provides generic tracefs/ftrace lifecycle support for TCP-AO selftests. It mounts a private tracefs, creates per-test tracing instances, runs reader threads on `trace_pipe`, and cleans up through registered destructors.

Important APIs and types: `struct test_ftracer` owns the pthread, instance path, trace pipe, callbacks, saved lines, condition variable, mutex, and linked-list node. Public functions include `create_ftracer`, `setup_trace_event`, `destroy_ftracer`, `tracer_get_savedlines_nr`, `tracer_get_savedlines`, `test_setup_tracing`, and `test_init_ftrace`.

Control flow: `test_init_ftrace` reads namespace cookies and probes ftrace support. `test_setup_tracing` ensures cookies differ, registers cleanup, mounts tracefs under a `ksft-ftrace-XXXXXX` temp directory, and calls TCP-AO-specific setup. `create_ftracer` creates an instance, disables trace options, sets buffer size, allocates saved-line storage, starts a trace reader thread, and links it into the global tracer list. Destruction waits briefly for expected events, cancels and joins the thread, removes the instance, and calls the caller's destructor.

State and persistence: global state includes `ftrace_path`, `ftrace_mounted`, namespace cookies, and a locked linked list of active tracers. Tracefs mount and instances are temporary filesystem state removed by cleanup. Saved trace lines are in-memory diagnostics.

Dependencies and integration points: depends on tracefs mount permission, pthreads, namespace switching helpers, `SO_NETNS_COOKIE`, `test_echo`, and TCP-AO event setup from `ftrace-tcp.c`.

Risks: tracefs mounting and unmounting require privileges and can fail in constrained environments. The tracer thread intentionally cancels blocking `getline`; cleanup must run to avoid leaked mounts. Buffer overflow is handled by stopping when saved-line capacity is reached, which can hide later events while preserving a diagnostic.

Test signals: ftrace setup success enables tracepoint validation. Cleanup reports tracer errors, unexpected thread termination, unmount/remove failures, and missing expected events through test logging.
