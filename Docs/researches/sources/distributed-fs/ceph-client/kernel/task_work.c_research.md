# sources/distributed-fs/ceph-client/kernel/task_work.c

## Purpose
`task_work.c` implements per-task callback queues that run at safe task transition points such as return to userspace, guest entry, or task exit. It is a lightweight mechanism for subsystems to defer work to the context of a specific task.

## Important APIs, types, and functions
- `task_work_add()`: atomically pushes a `struct callback_head` onto a task's LIFO work list and optionally notifies the task.
- `task_work_cancel_match()`, `task_work_cancel_func()`, `task_work_cancel()`: remove pending work by predicate, function, or exact callback.
- `task_work_run()`: drains the current task's callbacks and marks the list exited during task exit.
- `work_exited`: sentinel preventing new work on exiting/exited tasks.
- Optional IRQ work `irq_work_NMI_resume` supports `TWA_NMI_CURRENT`.

## Control flow
Adding work validates NMI mode, records KASAN auxiliary stack for normal modes, reads the current list head, fails on `work_exited`, and uses `try_cmpxchg()` to push the work. It then sets notify-resume, notify-signal, no-IPI signal, or NMI irq-work wakeup depending on mode. Cancellation locks `task->pi_lock`, walks the list, and removes a matching node with compare/exchange while tolerating races with add/run. Running work repeatedly detaches the whole list, optionally swaps in `work_exited` if the task is exiting and the list is empty, synchronizes with cancellation through `pi_lock`, invokes callbacks, and reschedules between callbacks.

## State and persistence behavior
State is stored in `task_struct::task_works` until callbacks run or are cancelled. The list is LIFO and not persisted beyond task lifetime. `work_exited` is a static sentinel only distinguished by address.

## Dependencies and integration points
The file integrates with `resume_user_mode`, signal/notify flags, IRQ work for NMI wakeups, spinlocks, KASAN stack recording, and scheduler rescheduling. It is used by io_uring, file/task cleanup, posix CPU timers in some configs, and other code needing task-context callbacks.

## Risks
There is no FIFO ordering guarantee. Callers must keep callback storage valid until execution or cancellation. Adding to exiting tasks fails with `-ESRCH`, so callers need fallback cleanup. Cancellation races are carefully handled but only remove pending work, not callbacks already detached and running.

## Test signals
Exercise callback add/run/cancel under task exit, return-to-user, signal notification, NMI-current mode with `CONFIG_IRQ_WORK`, and race tests between cancellation and run. KASAN/KCSAN and lockdep can expose lifetime and synchronization errors.
