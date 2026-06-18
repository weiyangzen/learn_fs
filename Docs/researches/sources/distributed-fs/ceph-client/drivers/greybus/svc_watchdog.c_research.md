# sources/distributed-fs/ceph-client/drivers/greybus/svc_watchdog.c

## Purpose

`svc_watchdog.c` implements a periodic SVC liveness watchdog. It pings the SVC every two seconds while enabled, disables itself around system suspend, and reacts to ping failure by either panicking the kernel or scheduling a userspace UniPro reset helper depending on `svc->action`.

## Important APIs, Types, and Functions

- `struct gb_svc_watchdog` stores delayed work, SVC pointer, enabled flag, and PM notifier.
- `gb_svc_watchdog_create()` allocates the watchdog, registers the PM notifier, and enables periodic pinging.
- `gb_svc_watchdog_destroy()` unregisters the notifier, disables work, clears `svc->watchdog`, and frees memory.
- `gb_svc_watchdog_enabled()`, `gb_svc_watchdog_enable()`, and `gb_svc_watchdog_disable()` implement sysfs-facing state control.
- `do_work()` performs the periodic `gb_svc_ping()` and schedules the next period if still enabled.
- `greybus_reset()` invokes `/system/bin/start unipro_reset` through `call_usermodehelper()` after reset-mode failure handling.
- `svc_watchdog_pm_notifier()` disables on `PM_SUSPEND_PREPARE` and reenables on `PM_POST_SUSPEND`.

## Control Flow

Creation initializes delayed work and stores the SVC pointer before registering the PM notifier and enabling the first delayed run. Each work execution pings SVC. On success it reschedules itself. On failure, panic action immediately calls `panic()`, while reset action schedules a separate delayed reset work item and flips `enabled` false so the watchdog does not repeatedly fire while reset tears down Greybus.

## State and Persistence Behavior

The watchdog persists as long as the registered SVC device exists. `enabled` gates periodic rescheduling but is not protected by a lock; calls usually occur from sysfs, PM notifier, and the delayed work context. A file-scope `reset_work` is shared across watchdog instances, which fits one active SVC expectation but is global state.

## Dependencies and Integration Points

The file depends on `gb_svc_ping()` from `svc.c`, Linux delayed work, PM notifiers, suspend events, panic/reset policy stored in `struct gb_svc`, and Android-like userspace path `/system/bin/start`.

## Risks and Edge Cases

- `enabled` is unsynchronized, so concurrent enable/disable/work execution can race, although delayed-work cancellation handles the common disable path.
- `reset_work` is global, so multiple SVC instances would share reset scheduling.
- The reset path hard-codes `/system/bin/start unipro_reset`; non-Android systems may not have it.
- PM notifier reenables unconditionally after suspend even if a user had disabled the watchdog before suspend.
- Destroy cancels watchdog work but not necessarily the global `reset_work` already scheduled.

## Test Signals

Cover create/destroy, sysfs enable/disable idempotence, ping success rescheduling, ping failure panic policy under controlled test hooks, reset policy scheduling and self-disable, suspend/resume notifier behavior, destroy while work is queued, and behavior when userspace reset helper is absent.
