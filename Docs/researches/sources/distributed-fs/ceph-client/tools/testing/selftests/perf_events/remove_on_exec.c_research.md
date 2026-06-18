# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/remove_on_exec.c

Purpose: tests `perf_event_attr.remove_on_exec` combined with inherited `sigtrap` events. It ensures forked children inherit events, but execed children have inherited events removed without affecting parent or non-exec siblings.

Important APIs/functions: `make_event_attr()` creates an inherited hardware instructions event with `remove_on_exec=1` and `sigtrap=1`. `sigtrap_handler()` counts `TRAP_PERF` signals. Fixture installs SIGTRAP handler and opens the event with `PERF_FLAG_FD_CLOEXEC`. `exec_child()` is the exec target selected by `argv[0] == "exec_child"`.

Control flow: `fork_only` verifies a forked child can enable the inherited event and trigger SIGTRAP. `fork_exec_then_enable` forks one non-exec child and one exec child, waits for the exec child to spin, enables the event, verifies exec child remains alive until killed, and confirms parent/non-exec child still receive events. `enable_then_fork_exec` enables before fork+exec and expects no trap in the exec child. `exec_stress` repeats fork+exec with mixed disabled/enabled timing.

State and persistence: creates children, pipes, signal handlers, and a perf fd; no persistent files. Exec uses `/proc/self/exe`.

Dependencies/integration: needs perf hardware instruction event access, procfs, SIGTRAP `TRAP_PERF` definitions from kernel headers, and signal delivery.

Risks: busy waits on `signal_count` can hang if perf events never fire after setup succeeds. Hardware counter availability and perf permissions may vary. It intentionally kills exec children.

Test signals: kselftest assertions plus hangs/timeouts in buggy cases; exec children should remain running until killed if remove-on-exec works.
