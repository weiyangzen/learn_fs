<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_assoc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_assoc.c

Purpose: tests explicit association between BPF programs and struct_ops maps, reuse of operator programs, and struct_ops calls from timer callbacks with and without a user reference.

Important APIs/types/functions: `bpf_program__assoc_struct_ops()`, skeleton attach helpers, `bpf_prog_test_run_opts()`, `bpf_map__attach_struct_ops()`, `sched_yield()`, and BSS fields such as `test_err_a`, `test_err_b`, `timer_cb_run`, `timer_test_1_ret`, and `timer_ns`.

Control flow: `test_st_ops_assoc()` verifies direct struct_ops callback association is rejected, associates syscall/tracing programs with maps A/B, rejects reassociation, attaches, triggers tracing through `sys_gettid()`, then test-runs syscall programs. Reuse subtest associates two syscall programs and checks both. Timer subtests run a syscall program that calls a kfunc and schedules a timer callback; the no-user-reference variant destroys link and closes fds before the delayed callback runs.

State and persistence: struct_ops links, map/program fds, timer callback state, and BSS error/result fields. No durable state beyond loaded BPF objects.

Dependencies and integration: depends on generated struct_ops skeletons, kernel kfuncs for multi struct_ops testing, timers, and bpf_testmod-style struct_ops support. Integrated as `test_struct_ops_assoc`.

Risks: busy-wait loops rely on timer callback completion. Closing fds intentionally tests lifetime/refcount behavior and could expose use-after-free regressions. Association APIs are libbpf-sensitive.

Test signals: expected success/error from association calls, attach success, zero error fields, syscall test-run success, timer return `1234` with reference and `-1` after dropped user reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_assoc.c -->
