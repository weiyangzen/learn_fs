# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-ops.c

Purpose: self-test style module showing custom `ftrace_ops` registration, filter setup, optional register saving, recursion/RCU assist flags, and hit-count validation.

Important APIs/functions: module params `nr_function_calls`, `nr_ops_relevant`, `nr_ops_irrelevant`, `save_regs`, `assist_recursion`, `assist_rcu`, `check_count`, and `persist`; `struct ftrace_ops`; `ftrace_set_filter_ip`; `register_ftrace_function`; `unregister_ftrace_function`; local `tracee_relevant` and `tracee_irrelevant`.

Control flow: init allocates arrays of relevant and irrelevant ops, configures each with filter IP and flags, registers them, calls tracee functions repeatedly, optionally verifies hit counts, and unregisters unless `persist` is requested. Exit unregisters/destroys persistent ops.

State and persistence: allocated `sample_ops` arrays and per-op call counters. Persist mode intentionally leaves registrations active until module exit.

Dependencies and integration: integrates with core ftrace callback API, not direct trampolines.

Risks: bad parameter values can allocate many ops and create tracing overhead. `persist` changes lifecycle. Count checks can fail if callbacks are missed or tracing semantics change.

Test signals: load with small counts and `check_count=1`, verify success or expected warnings; try `save_regs`, `assist_recursion`, and `persist` combinations.
