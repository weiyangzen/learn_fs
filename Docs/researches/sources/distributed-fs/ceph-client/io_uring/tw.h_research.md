# sources/distributed-fs/ceph-client/io_uring/tw.h

Purpose: declares task-work helpers and inline routing logic for normal vs deferred io_uring task_work.

Important APIs/types/functions: `IO_LOCAL_TW_DEFAULT_MAX`, `io_should_terminate_tw()`, task-work add/run/fallback prototypes, `__io_req_task_work_add()`, `io_req_task_work_add()`, `io_run_task_work()`, `io_local_work_pending()`, `io_task_work_pending()`, `io_tw_lock()`, `io_allowed_defer_tw_run()`, and `io_allowed_run_tw()`.

Control flow: inline routing sends requests to local ring work when `IORING_SETUP_DEFER_TASKRUN` is set, otherwise to task work. `io_run_task_work()` clears notify signals, handles PF_IO_WORKER resume/task lists, and runs generic task_work. Permission helpers enforce that deferred work is run by the submitter task.

State and persistence: manipulates current task notify state and observes ring local-work lists; no state is declared beyond constants.

Dependencies/integration: includes scheduler, percpu refcount, and io_uring types; used throughout completion, poll, timeout, wait, and command paths.

Risks/test signals: incorrect inline routing causes missed completions or wrong-task execution. Tests with `DEFER_TASKRUN`, io-wq workers, and task exit cover this.
