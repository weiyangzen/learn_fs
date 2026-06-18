# sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal.c

Purpose: `bp_signal.c` tests signal delivery and resume-flag behavior for hardware breakpoint and watchpoint overflow notifications.

Important APIs and state: three global fds represent a breakpoint on `__test_function`, a breakpoint on the signal handler, and a watchpoint on `the_var`. `sig_handler` and `sig_handler_2` count nested notifications and disable events if recursion runs away. `__event` configures async perf events with `F_SETSIG` and `F_SETOWN`.

Control flow: after architecture support checks, the test installs SIGIO and SIGUSR1 handlers, creates the three events, enables them, and calls `test_function`. Expected execution triggers one primary breakpoint, nested handler breakpoints, and two watchpoint hits. It disables events, reads counts, closes fds, and validates counts and overflow counters exactly.

State and persistence: state is global counters and event descriptors for the test duration only. No files are written.

Dependencies, integration, risks, and tests: it depends on debug-register support, async signal delivery, architecture-specific inline assembly on x86_64, and perf_event permissions. Risks include flaky behavior under signal restrictions, unsupported architectures, and false failures if RF EFLAG or nested signal behavior changes intentionally. Test signals are count1=1, count2=3, count3=2, overflows=3, and overflows_2=3.
