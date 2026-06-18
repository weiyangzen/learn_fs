# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_dev.c

## Purpose
`watchdog_dev.c` is the generic Linux watchdog character-device layer. It turns registered `struct watchdog_device` instances into `/dev/watchdogN`, preserves the legacy `/dev/watchdog` miscdevice for watchdog0, exposes optional sysfs attributes, drives standard watchdog ioctls, and supplies framework-managed keepalive/pretimeout timers for hardware with shorter heartbeat limits than the user-visible timeout.

## Important APIs, types, and functions
The main internal state is `struct watchdog_core_data`, attached through `wdd->wd_data`, with a device/cdev, mutex, status bits, hrtimer, kthread work, last keepalive timestamps, and open deadline. Public entry points are `watchdog_dev_register`, `watchdog_dev_unregister`, `watchdog_dev_init`, `watchdog_dev_exit`, `watchdog_set_last_hw_keepalive`, `watchdog_dev_suspend`, and `watchdog_dev_resume`. Key helpers include `watchdog_start`, `watchdog_stop`, `watchdog_ping`, `__watchdog_ping`, `watchdog_set_timeout`, `watchdog_set_pretimeout`, `watchdog_get_timeleft`, `watchdog_cdev_register`, and `watchdog_cdev_unregister`.

## Control flow
Module init creates the FIFO-priority `watchdogd` kthread worker, registers the watchdog class, and allocates major/minor space. Device registration allocates core data, initializes keepalive and pretimeout timers, adds a cdev/device, and for id 0 registers the legacy miscdevice. Opening the node single-opens the device, pins the owner module when needed, starts hardware, and disables the pre-userspace open deadline. Writes scan for magic close character `V` and ping. Ioctls first defer to a driver-specific ioctl, then implement common `WDIOC_*` operations. Release stops only on magic close or non-magicclose devices; otherwise it pings and leaves hardware running.

## State and persistence
State is runtime-only: device open bits, magic-close permission, `WDOG_ACTIVE`/`WDOG_HW_RUNNING`, module/device references, open deadline, last userspace and hardware keepalive times, and hrtimers. The keepalive worker persists while hardware is running before userspace takes over or while a virtual timeout exceeds hardware `max_hw_heartbeat_ms`. No on-disk persistence exists.

## Dependencies and integration points
It integrates the watchdog core, character-device layer, miscdevice compatibility, sysfs, module lifetime, hrtimers, kthread work, tracepoints, and pretimeout governors. Driver callbacks in `wdd->ops` provide hardware start/stop/ping/status/timeout behavior. `handle_boot_enabled` and `open_timeout` module parameters control early boot handling for already-running hardware watchdogs.

## Risks and test signals
Risks include lifetime races between unregister and open/release, incorrect module pinning when hardware remains running, timer scheduling around min/max heartbeat bounds, magic-close semantics, nowayout immutability, and pretimeout timer cancellation during stop/unregister/suspend. Test signals include concurrent open attempts, unregister while open, already-running hardware with finite open timeout, virtual timeout greater than hardware timeout, all standard watchdog ioctls, sysfs visibility with and without pretimeout support, suspend/resume pings, and nowayout release behavior.
