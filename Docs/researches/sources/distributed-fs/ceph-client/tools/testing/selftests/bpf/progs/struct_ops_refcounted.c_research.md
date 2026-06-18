<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted.c

Purpose: Positive verifier test for referenced `task_struct *` arguments passed into struct_ops callbacks.

Important APIs/types/functions: Defines a `test_refcounted` callback that releases the task on both branches and a linked map.

Control flow: The callback receives a referenced task pointer and releases exactly once regardless of branch.

State and persistence: No durable state aside from the map link.

Dependencies and integration: Depends on bpf_testmod refcounted op and `bpf_task_release` kfunc.

Risks: Reference ownership must be tracked across branch joins.

Test signals: Pass signal is verifier acceptance and no reference leak.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted.c -->
