# sources/distributed-fs/ceph-client/io_uring/tw.c

Purpose: implements io_uring task_work routing, local deferred task_work for `DEFER_TASKRUN`, fallback workqueue execution, and bounded local task_work runs.

Important APIs/types/functions: `io_fallback_req_func()`, `io_handle_tw_list()`, `tctx_task_work_run()`, `tctx_task_work()`, `io_req_local_work_add()`, `io_req_normal_work_add()`, `io_req_task_work_add_remote()`, `io_move_task_work_from_local()`, `io_run_local_work_locked()`, and `io_run_local_work()`.

Control flow: normal mode queues request task_work to the submitting task's `task_list` and uses kernel task_work notification, except SQPOLL runs it itself. Deferred mode pushes requests to the ring local llist, marks `IORING_SQ_TASKRUN`, signals eventfd if needed, and wakes the submitter based on `cq_wait_nr` and lazy-wake counts. Runners group work by ctx, hold `uring_lock`, take ctx refs, compute cancellation state, invoke request callbacks through indirect-call optimized paths, flush completions, and reschedule if needed. Fallback moves abandoned task_work to delayed work when task_work cannot be queued or task exits.

State and persistence: transient state includes task llists, ring local/retry/fallback llists, `IORING_SQ_TASKRUN`, `cq_wait_nr`, request `nr_tw`, ctx refs, and delayed fallback work. It persists only while completions/retries are pending.

Dependencies/integration: integrates with task_work, io-wq workers, SQPOLL, eventfd, wait logic, poll and rw completion callbacks, local-work wait wakeups, and ring teardown.

Risks/test signals: risks are lost wakeups, running task_work on the wrong task, fallback ref leaks, cancellation during ring teardown, and starvation when capping local work. Test deferred taskrun waits, SQPOLL task_work, eventfd wakeups, task exit fallback, linked requests disabling lazy wake, and stress with many completions.
