<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_work.h -->
# sources/distributed-fs/ceph-client/include/linux/task_work.h

## Purpose
declares task-work callbacks: small deferred callbacks attached to a task and run on return-to-user, signal delivery, NMI-current, or explicit task-work drain paths.

## Important APIs, Types, and Functions
The file is 44 lines and exports these visible symbol families: types/enums `task_work_notify_mode`, `callback_head`; macros/constants none; function-like macros none; inline helpers `init_task_work`, `task_work_pending`, `exit_task_work`; external prototypes `void`, `READ_ONCE`, `task_work_add`, `task_work_cancel`, `task_work_run`.

## Control Flow
A callback head is initialized with `init_task_work()`, queued with `task_work_add()` using a notify mode, optionally cancelled by callback or match function, and executed by `task_work_run()` at safe task checkpoints. `exit_task_work()` drains pending work during task exit.

## State and Persistence Behavior
Pending work is held on `task_struct::task_works`; `task_work_pending()` reads that pointer. Callback ownership transfers to the task-work machinery once successfully queued.

## Dependencies and Integration Points
It depends on callback_head/list and scheduler task structures. It integrates with io_uring, fput/deferred file cleanup, task exit, signal/resume hooks, and architecture return-to-user notification. Direct includes are `linux/list.h`, `linux/sched.h`.

## Risks and Edge Cases
Callbacks run in the target task context and must handle cancellation, exit, and ordering carefully. Queuing to exiting tasks or assuming immediate execution can leak resources or defer cleanup too long.

## Test Signals
Exercise each notify mode, cancellation by function and predicate, exit draining, nested callback addition, and races with task exit and signal delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_work.h -->
