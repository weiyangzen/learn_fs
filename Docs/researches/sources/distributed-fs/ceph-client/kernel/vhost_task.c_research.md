<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vhost_task.c -->
# sources/distributed-fs/ceph-client/kernel/vhost_task.c

Purpose: creates and manages specialized user-worker tasks for vhost. These tasks run a caller-provided work function in a loop, share selected process resources, and handle stop versus SIGKILL races.

Important APIs and state: `vhost_task_create()` allocates the wrapper and uses `copy_process()` with user-worker clone args. `vhost_task_start()` wakes the new task. `vhost_task_wake()` wakes a running task. `vhost_task_stop()` requests stop, waits for exit, drops task ref, and frees the wrapper. `struct vhost_task` stores callbacks, data, completion, flags, task pointer, and `exit_mutex`.

Control flow: the worker loop consumes pending signals, sets interruptible state, exits if STOP is set, calls `fn(data)`, and schedules when no work was done. On exit it serializes with `vhost_task_stop()`; if STOP was not set, it marks KILLED and calls `handle_sigkill(data)`, then completes and exits.

State and persistence: lifecycle state is in STOP and KILLED bits plus the completion. The wrapper persists from create until stop frees it. The task is inactive until explicitly started.

Dependencies and integration: depends on kernel clone internals, user-worker task flags, completions, signals, scheduler wakeups, and vhost layer callbacks.

Risks: stop and SIGKILL race handling is central; vhost stop assumes upper layers have stopped new work and flushed before freeing. Callback `fn` must cooperate by returning false when idle. Test signals include create/start/stop, wakeups from idle, SIGKILL handling before stop, concurrent stop and signal, callback work/no-work behavior, and copy_process failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vhost_task.c -->
