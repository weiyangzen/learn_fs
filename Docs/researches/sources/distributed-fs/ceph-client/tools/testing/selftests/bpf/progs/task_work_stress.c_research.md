<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_stress.c

Purpose: Stress test for scheduling and deleting BPF task work through syscall programs.

Important APIs/types/functions: Defines hash map `hmap`, callback `process_work`, and syscall programs `schedule_task_work` and `delete_task_work`.

Control flow: One syscall path schedules task work from map values; the other deletes entries to stress cancellation/lifetime races.

State and persistence: Persistent state is the hash map and scheduled task-work objects.

Dependencies and integration: Depends on syscall program type and task-work kfunc support.

Risks: Races between deletion and deferred callback are the main risk.

Test signals: Stress harness repeatedly schedules/deletes and checks for stable execution/errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_stress.c -->
