# sources/distributed-fs/ceph-client/kernel/power/process.c

## Purpose
Implements task and workqueue freezing/thawing for suspend and hibernation transitions. It stops user tasks, freezable kernel threads, and freezable workqueues so memory images and low-power transitions happen from a quiescent task state.

## Important APIs, Types, and Functions
Global `freeze_timeout_msecs` defaults to 20 seconds and is exposed through `/sys/power/pm_freeze_timeout` in `main.c`. `try_to_freeze_tasks(bool user_only)` is the core loop. Public entry points are `freeze_processes()`, `freeze_kernel_threads()`, `thaw_processes()`, and `thaw_kernel_threads()`.

The implementation uses `pm_freezing`, `pm_nosig_freezing`, the `freezer_active` static key, `PF_SUSPEND_TASK`, `__usermodehelper_disable()`, `__usermodehelper_set_disable_depth()`, `usermodehelper_enable()`, `oom_killer_disable()`, `oom_killer_enable()`, `freeze_task()`, `frozen()`, `freezing()`, freezable workqueue helpers, and tracepoint `trace_suspend_resume()`.

## Control Flow
`freeze_processes()` disables usermode helpers in freezing mode, marks the current task as `PF_SUSPEND_TASK`, activates the freezer static key, clears wakeup state, sets `pm_freezing`, and calls `try_to_freeze_tasks(true)`. On success it fully disables usermode helpers and disables the OOM killer with the same timeout budget. On failure it thaws all processes.

`freeze_kernel_threads()` sets `pm_nosig_freezing` and calls `try_to_freeze_tasks(false)`, which additionally begins and polls freezable workqueue freezing. Failure thaws only kernel threads/workqueues, leaving user-space thawing to the caller.

`try_to_freeze_tasks()` repeatedly walks all process threads under `tasklist_lock`, calls `freeze_task()`, counts tasks still needing the refrigerator, adds workqueue busy state, backs off sleeps from 1 ms to 8 ms, and aborts on timeout or `pm_wakeup_pending()`. It prints refusing tasks and freezable workqueues when debugging or non-wakeup failure occurs.

`thaw_processes()` disables freezer state, re-enables the OOM killer and usermode helpers, thaws workqueues and all tasks, clears `PF_SUSPEND_TASK` on the current task, schedules once, and emits trace/log messages. `thaw_kernel_threads()` clears kernel-thread freezing and thaws only `PF_KTHREAD` tasks plus workqueues.

## State and Persistence Behavior
Freezer state is transient but globally visible while a transition is active. `PF_SUSPEND_TASK` prevents the initiating task from freezing itself. Usermode-helper disable depth and OOM killer state must be restored on every error path. No persistent on-disk state is created.

## Dependencies and Integration Points
This file integrates with the scheduler, freezer subsystem, workqueues, usermode helper infrastructure, OOM killer, wakeup-source detection, tracepoints, and suspend/hibernate orchestration. `suspend.c`, `hibernate.c`, and `user.c` rely on these calls for both normal kernel-driven transitions and `/dev/snapshot` flows.

## Risks
Risks include deadlocks from tasks refusing to freeze, freezer state leaks after partial failure, OOM killer left disabled, usermode helpers left at the wrong depth, wakeup events aborting without enough diagnostic signal, and workqueue freezing regressions. The task walk runs under `tasklist_lock`, so changes must avoid sleeping while holding it.

## Test Signals
Use `/sys/power/pm_test=freezer`, hibernation freezer tests, deliberate non-freezable tasks, freezable workqueue workloads, wakeup-event injection during freezing, OOM-victim scenarios, and usermode-helper activity during suspend. Verify thaw paths restore usermode helpers, OOM killer, workqueues, and `PF_SUSPEND_TASK`.
