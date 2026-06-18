# sources/distributed-fs/ceph-client/include/linux/resume_user_mode.h

Purpose: this header defines generic work that must run just before a task resumes user mode after `TIF_NOTIFY_RESUME`.

Important APIs/types/functions: `set_notify_resume(struct task_struct *task)` sets `TIF_NOTIFY_RESUME` and kicks the process if the flag was newly set. `resume_user_mode_work(struct pt_regs *regs)` clears the flag, runs pending task work, drops cached requested keys, handles memcg over-high throttling, maybe throttles blkcg, and handles rseq slow paths.

Control flow: kernel code calls `set_notify_resume()` when a task needs return-to-user work. Architecture exit-to-user code sees `TIF_NOTIFY_RESUME`, clears it before invoking `resume_user_mode_work()`, and may repeat if another asynchronous setter races. A memory barrier pairs with `task_work_add()` list insertion before checking `task_work_pending(current)`.

State and persistence: persistent state is the thread flag and queued task work on `task_struct`; cached key, memcg, blkcg, and rseq state are updated for the current task. The function itself stores no state.

Dependencies and integration points: depends on scheduler/thread flags, task_work, key request cache, memcg, blk-cgroup, restartable sequences, and architecture return-to-user paths.

Risks: missing the memory barrier or clearing the flag incorrectly can lose task_work execution. This code runs without locks, so called helpers must handle their own synchronization and may affect latency on return to user. Test signals include task_work execution before user return, rseq abort/signal tests, memcg over-high throttling, cached key cleanup, and architecture exit-path tests.
