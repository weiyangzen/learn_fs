<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_uptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_uptr.c

Purpose: Tests task local storage values containing user pointers.

Important APIs/types/functions: Defines `datamap`, local task/task_struct declarations, and `tp_btf/sys_enter` handler `on_enter`.

Control flow: Handler associates data with the current task and manipulates or checks a user pointer stored in map value.

State and persistence: Persistent state is the task local storage map.

Dependencies and integration: Depends on task storage helper support for values with user-pointer fields.

Risks: Verifier must track user pointers in storage without treating them as trusted kernel pointers.

Test signals: Test signal is successful load and expected storage value behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_ls_uptr.c -->
