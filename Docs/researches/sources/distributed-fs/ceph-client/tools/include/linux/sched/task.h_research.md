<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/task.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sched/task.h

## Purpose
This is an empty compatibility header for task-lifetime scheduler includes in the tools tree.

## APIs And Flow
It defines only an include guard. It does not provide `task_struct`, clone helpers, task refcounting, or scheduler callbacks.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration is include-level compatibility for code paths that avoid task APIs in user space. Risks are compile failures if new imported code uses kernel task lifetime interfaces. Test signals are full tools builds and static checks that no `sched/task.h` symbols are referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/task.h -->
