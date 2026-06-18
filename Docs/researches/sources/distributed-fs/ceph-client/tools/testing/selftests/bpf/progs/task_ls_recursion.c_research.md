<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_recursion.c

Purpose: Tests recursion protection for task local storage when storage helper internals are traced.

Important APIs/types/functions: Defines two maps, an `fentry/bpf_local_storage_update` program, and `tp_btf/sys_enter` program.

Control flow: The sys_enter path updates task storage; the fentry hook observes helper execution and tries guarded storage interactions to ensure recursion is handled.

State and persistence: Persistent state is `map_a`, `map_b`, and globals/counters.

Dependencies and integration: Depends on task local storage helpers and fentry tracing of helper-like kernel functions.

Risks: Uncontrolled recursion can deadlock or corrupt storage state.

Test signals: Tests expect bounded execution and correct counters rather than recursive failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_recursion.c -->
