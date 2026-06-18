<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_storage_nodeadlock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_storage_nodeadlock.c

Purpose: Tests task storage operations from sleepable LSM `socket_post_create` context for deadlock avoidance.

Important APIs/types/functions: Defines `task_storage` and `lsm.s/socket_post_create` program.

Control flow: The LSM hook performs task storage access when sockets are created.

State and persistence: Persistent state is task storage bound to current task.

Dependencies and integration: Depends on sleepable LSM hooks and local storage locking.

Risks: Lock ordering between task storage and socket/LSM paths is the risk.

Test signals: Passing tests create sockets and see no deadlock plus expected storage result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_storage_nodeadlock.c -->
