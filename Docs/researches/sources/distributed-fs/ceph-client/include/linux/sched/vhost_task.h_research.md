# sources/distributed-fs/ceph-client/include/linux/sched/vhost_task.h

Purpose: declares the vhost task abstraction used to run vhost work in scheduler-managed task context.

Important APIs and types: opaque `struct vhost_task`, `vhost_task_create()`, `vhost_task_start()`, `vhost_task_stop()`, and `vhost_task_wake()` are the interface.

Control flow: vhost code creates a task with a work function and kill handler, starts it, wakes it when work is available, and stops it during teardown.

State and persistence: vhost task state is owned by the implementation and persists between create/start and stop/destruction.

Dependencies and integration points: integrates vhost drivers with task creation, scheduler wakeups, and signal/kill handling without exposing implementation details.

Risks and test signals: risks include wake after stop, kill-handler ordering, task lifetime leaks, and work function return semantics. Test vhost device start/stop, teardown under load, wake races, and signal/kill paths.
