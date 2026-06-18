# sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal_overflow.c

Purpose: `bp_signal_overflow.c` verifies breakpoint sample-period overflow delivery through SIGIO.

Important APIs and state: constants define execution count and overflow threshold. A global fd and overflow counter are used by the SIGIO handler. `test_function` is the breakpoint target, and `bp_count` reads the final event count.

Control flow: the test installs a SIGIO handler, configures a disabled instruction breakpoint with `sample_period = THRESHOLD` and async notification, enables it, executes the target function `EXECUTIONS` times, disables it, reads the count, and compares both total executions and overflow notifications with expected values.

State and persistence: kernel event state exists only while the fd is open. The software state is the overflow counter.

Dependencies, integration, risks, and tests: it depends on hardware instruction breakpoint support and signal delivery. Risks include unsupported architectures, perf_event permissions, and noisy signal behavior if events are not disabled promptly. Test signals are final count equal to `EXECUTIONS` and overflows equal to `EXECUTIONS / THRESHOLD`.
