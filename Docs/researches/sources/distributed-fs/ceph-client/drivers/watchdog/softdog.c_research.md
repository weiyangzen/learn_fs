# sources/distributed-fs/ceph-client/drivers/watchdog/softdog.c

## Purpose
`softdog.c` implements a software-only watchdog using high-resolution timers. On expiry it can ignore reboot, panic, emergency restart, or run a configured reboot command before falling back to emergency restart. It also optionally supports pretimeout notification.

## Important APIs, types, and functions
Module parameters are `soft_margin`, `nowayout`, `soft_noboot`, `soft_panic`, `soft_reboot_cmd`, and `soft_active_on_boot`. Main timers are `softdog_ticktock` and optional `softdog_preticktock`. Important callbacks are `softdog_fire()`, `softdog_pretimeout()`, `softdog_ping()`, `softdog_stop()`, `reboot_work_fn()`, and `reboot_kthread_fn()`. `softdog_dev` is the registered watchdog.

## Control flow
Init validates/configures timeout via `watchdog_init_timeout()`, applies nowayout and stop-on-reboot, initializes timers, optionally starts immediately, then registers the watchdog. Starting and pinging are the same operation: the expiry hrtimer is armed for `w->timeout`, and the module refcount is acquired if the timer was previously inactive. Expiry releases that refcount and performs the configured action. If a reboot command is used, work launches a kernel thread and the timer is extended by the default margin to force emergency restart if orderly restart stalls.

## State and persistence behavior
State is entirely volatile: hrtimer active state, module reference count, and the static `soft_reboot_fired` guard. There is no hardware persistence, so it cannot recover from CPU lockups, interrupt-disabled stalls, or scheduler failures except where the expiry path still runs.

## Dependencies and integration points
The driver integrates with watchdog core, hrtimers, workqueues, kthreads, `kernel_restart()`, `emergency_restart()`, and optional `CONFIG_SOFT_WATCHDOG_PRETIMEOUT`.

## Risks and test signals
Risks include giving a false sense of hardware recovery, module refcount imbalance if timer paths change, pretimeout calculation when pretimeout exceeds timeout, and reboot-command path needing scheduler/workqueue progress. Tests should cover init parameter ranges, start/stop reference behavior, expiry modes, `soft_active_on_boot`, pretimeout notification, nowayout close behavior through the core, and emergency fallback after a reboot command.
