# sources/distributed-fs/ceph-client/drivers/char/hangcheck-timer.c

## Purpose
`hangcheck-timer.c` implements a lightweight hang detector. It periodically schedules a kernel timer, compares actual elapsed monotonic nanoseconds against configured tick plus margin, optionally dumps task state, and optionally reboots via `emergency_restart()`.

## Important APIs, Types, and Functions
- Module parameters: `hangcheck_tick`, `hangcheck_margin`, `hangcheck_reboot`, and `hangcheck_dump_tasks`.
- Built-in boot options: `hcheck_tick`, `hcheck_margin`, `hcheck_reboot`, and `hcheck_dump_tasks`.
- `hangcheck_fire()` is the timer callback and main decision point.
- `hangcheck_init()` computes the nanosecond margin and arms `hangcheck_ticktock`.
- `hangcheck_exit()` deletes the timer synchronously.

## Control Flow
Init computes `(hangcheck_tick + hangcheck_margin) * 1e9`, records `ktime_get_ns()`, and schedules the timer for `hangcheck_tick * HZ`. Each callback computes elapsed time since the last recorded callback. If elapsed exceeds the margin, it may print SysRq task state and either reboot or log a critical warning. It then rearms the timer and records a new timestamp.

## State and Persistence Behavior
All state is in module parameters plus two global nanosecond counters. No userspace ABI or persistent storage is created. The timer state exists until module exit, where `timer_delete_sync()` prevents a callback from running after removal.

## Dependencies and Integration Points
It uses the kernel timer wheel, `ktime_get_ns()`, module parameters, `CONFIG_MAGIC_SYSRQ` task dump support, and `emergency_restart()`. It is intended for cluster fencing or systems that prefer a hard restart when scheduling stalls exceed a tolerance.

## Risks
The code is intentionally disruptive when `hangcheck_reboot` is enabled. Very large parameter values can overflow `jiffies + hangcheck_tick * HZ` or the nanosecond product. The wraparound fallback for `ktime_get_ns()` is theoretical because monotonic nanoseconds should not wrap in practical runtime.

## Test Signals
Build as module and built-in. Validate parameter parsing, timer arm/delete, warnings with reboot disabled, SysRq task dump under `CONFIG_MAGIC_SYSRQ`, and reboot path only in controlled test environments. Static tests should cover extreme tick/margin values.
