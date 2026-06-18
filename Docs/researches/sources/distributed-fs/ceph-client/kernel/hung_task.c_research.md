# sources/distributed-fs/ceph-client/kernel/hung_task.c

## Purpose
`hung_task.c` implements `khungtaskd`, the kernel watchdog that detects tasks stuck in uninterruptible sleep for too long. It emits diagnostics, optional all-CPU backtraces/system information, blocker ownership hints, counters visible through sysctl, and can panic when configured.

## Important APIs, types, and functions
Key globals are `sysctl_hung_task_timeout_secs`, `sysctl_hung_task_check_interval_secs`, `sysctl_hung_task_check_count`, `sysctl_hung_task_warnings`, `sysctl_hung_task_detect_count`, `sysctl_hung_task_panic`, `hung_task_si_mask`, `watchdog_task`, and suspend/panic flags. Important functions are `task_is_hung()`, `debug_show_blocker()`, `hung_task_info()`, `check_hung_uninterruptible_tasks()`, `proc_dohung_task_detect_count()`, `proc_dohung_task_timeout_secs()`, `reset_hung_task_detector()`, `hungtask_pm_notify()`, `watchdog()`, and `hung_task_init()`.

## Control flow
`khungtaskd` sleeps for the configured interval, then scans process threads under RCU unless reset or suspended. `task_is_hung()` filters for `TASK_UNINTERRUPTIBLE` tasks that are not killable, idle, or frozen and whose context switch count has not changed since the last check. Detected tasks increment the global counter, trigger tracepoints, print task and blocker diagnostics while warnings remain or panic is pending, update sys-info mask selection, and eventually call `panic()` if the per-round panic threshold is reached. The scan periodically breaks and reacquires RCU to avoid excessive grace-period and preemption latency.

## State and persistence
State is runtime-only: per-task `last_switch_count` and `last_switch_time`, global sysctl tunables, an atomic detection counter, warning budget, reset flag, suspend flag, and panic notification flag. Sysctl writes can reset the detect counter only by writing zero and wake the watchdog after timeout changes. No state persists beyond boot.

## Dependencies and integration points
The file integrates with scheduler task state, tracepoints, sysctl, panic notifiers, PM notifiers, freezer/suspend lifecycle, RCU task iteration, lock/blocker owner helpers for mutex/semaphore/rwsem, `sys_info()`, and NMI watchdog touch points. It exports `reset_hung_task_detector()` for subsystems that need to suppress false positives after long stalls.

## Risks and test signals
Risks include false positives during heavy stalls or suspend transitions, races while reading task state and blocker owners, warning suppression hiding later hangs, panic threshold semantics changing operator expectations, and scan count limits missing tasks. Test signals include sysctl interval and timeout updates, reset behavior, D-state task detection, TASK_KILLABLE/TASK_IDLE/TASK_FROZEN exclusion, blocker owner printing, suspend/resume suppression, all-CPU backtrace option, and panic-on-hung-task boot/sysctl settings.
