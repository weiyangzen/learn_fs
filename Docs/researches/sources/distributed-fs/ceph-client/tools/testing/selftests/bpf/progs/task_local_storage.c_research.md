<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage.c

Purpose: Tests task local storage creation and lookup across syscall enter/exit tracepoints.

Important APIs/types/functions: Defines `enter_id` map and `tp_btf/sys_enter`/`sys_exit` programs.

Control flow: Sys-enter stores data keyed by current task; sys-exit reads/removes or validates the stored value.

State and persistence: Persistent state is task-local storage plus the `enter_id` map/counters.

Dependencies and integration: Depends on task storage helpers and tracepoint BTF context.

Risks: Storage lifetime across syscall boundaries and task identity are the risks.

Test signals: Tests trigger syscalls and verify expected stored id/counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_local_storage.c -->
