# sources/distributed-fs/ceph-client/drivers/base/power/runtime.c

## Purpose
This file is the Linux device core runtime PM state machine. It implements the public `pm_runtime_*()` entry points, the internal suspend/resume/idle execution paths, autosuspend timers, runtime PM usage counting, parent/child accounting, device-link supplier coordination, wake IRQ handoff, and force-suspend/force-resume helpers used during system sleep transitions.

## Important APIs, Types, And Functions
The main internal callbacks are `rpm_idle()`, `rpm_suspend()`, and `rpm_resume()`, all called with `dev->power.lock` held and interrupts disabled. Public exports include `__pm_runtime_idle()`, `__pm_runtime_suspend()`, `__pm_runtime_resume()`, `pm_schedule_suspend()`, `__pm_runtime_set_status()`, `pm_runtime_barrier()`, `__pm_runtime_disable()`, `pm_runtime_enable()`, devres wrappers, `pm_runtime_forbid()`, `pm_runtime_allow()`, `pm_runtime_no_callbacks()`, `pm_runtime_irq_safe()`, autosuspend setters, supplier helpers, link helpers, and `pm_runtime_force_suspend()/pm_runtime_force_resume()`.

## Control Flow And State
The device state lives in `dev->power`: `runtime_status`, `last_status`, `disable_depth`, `usage_count`, `child_count`, `runtime_error`, `runtime_auto`, request fields, autosuspend timer fields, `deferred_resume`, `irq_safe`, `no_callbacks`, `needs_force_resume`, accounting timestamps, and supplier link counts. `rpm_check_suspend_allowed()` gates suspend on errors, disabled runtime PM, nonzero usage, active children, pending resumes, QoS latency, and current status. `rpm_suspend()` handles autosuspend expiration, request cancellation, concurrent suspend waits, wake IRQ enable sequencing, `runtime_suspend` callback execution, parent child-count decrement, supplier idling, deferred resume, and error rollback. `rpm_resume()` clears pending requests, waits or defers across concurrent state changes, resumes parents and suppliers, disables wake IRQs, calls `runtime_resume`, increments parent child-count, marks last busy, and queues an idle notification.

Asynchronous requests are stored as `RPM_REQ_*` and executed by `pm_runtime_work()` on `pm_wq`; delayed suspends are driven by an `hrtimer`. Accounting is updated before runtime status changes and exposed as active/suspended nanosecond totals.

## Dependencies And Integration Points
This file depends on `linux/pm_runtime.h`, `linux/pm_wakeirq.h`, hrtimers, device links, PM QoS, workqueues, `trace/events/rpm.h`, and driver/bus/class/type/PM-domain `dev_pm_ops`. Wake IRQ integration calls `dev_pm_enable_wake_irq_check()`, `dev_pm_enable_wake_irq_complete()`, and `dev_pm_disable_wake_irq_check()`. Device-link integration keeps suppliers active while consumers resume and releases them after suspend or failed resume. Sysfs `power/control` routes through `pm_runtime_allow()` and `pm_runtime_forbid()`.

## Risks And Test Signals
The main risks are unbalanced usage counts, parent child-count drift, callback return-code misuse, races around `RPM_ASYNC`/`RPM_NOWAIT`, improper `irq_safe` usage, and failure to call `regcache_mark_dirty()`-style driver hooks after power loss. Test signals include runtime PM selftests or driver tests that exercise suspend/resume failure, autosuspend rescheduling, supplier failure, wake IRQ ordering, `pm_runtime_barrier()` cancellation, usage-count underflow warnings, tracepoints (`rpm_*`), and sysfs status/time changes.
