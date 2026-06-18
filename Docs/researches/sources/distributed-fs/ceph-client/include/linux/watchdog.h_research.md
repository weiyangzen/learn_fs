# sources/distributed-fs/ceph-client/include/linux/watchdog.h

## Purpose
`watchdog.h` defines the generic Linux watchdog device interface for hardware and software watchdog drivers. It describes driver operations, registered watchdog device state, timeout validation helpers, lifecycle registration, suspend/resume, restart priority, and managed registration.

## Important APIs, Types, and Functions
`struct watchdog_ops` contains driver callbacks for `start`, optional `stop`, `ping`, `status`, timeout/pretimeout setters, time-left query, restart, and extra ioctl handling. `struct watchdog_device` stores ID, parent, sysfs groups, uapi info, ops, pretimeout governor, boot status, timeout/pretimeout bounds, hardware heartbeat bounds, notifier blocks, driver data, core data, status bits, PM notifier, and deferred-registration list. Status bits include `WDOG_ACTIVE`, `WDOG_NO_WAY_OUT`, `WDOG_STOP_ON_REBOOT`, `WDOG_HW_RUNNING`, `WDOG_STOP_ON_UNREGISTER`, and `WDOG_NO_PING_ON_SUSPEND`. Helpers include `watchdog_active()`, `watchdog_hw_running()`, nowayout/reboot/unregister/suspend flag setters, timeout/pretimeout validators, driver-data get/set, `watchdog_notify_pretimeout()`, `watchdog_set_restart_priority()`, `watchdog_init_timeout()`, register/unregister, suspend/resume, `watchdog_set_last_hw_keepalive()`, and `devm_watchdog_register_device()`.

## Control Flow
A driver fills `watchdog_device` and `watchdog_ops`, initializes timeout defaults, sets policy flags, and registers the device. Userspace opens/pings/sets timeouts through the watchdog core, which dispatches to driver callbacks. Reboot/restart and PM paths use notifier blocks and suspend/resume helpers. Pretimeout events either go through a governor or log an alert fallback.

## State and Persistence
State is runtime device state plus hardware watchdog state. `WDOG_HW_RUNNING` records a watchdog already running before registration; `WDOG_NO_WAY_OUT` can make stop impossible after start. Hardware may persist across reboot depending on platform, but this header defines only in-kernel representation.

## Dependencies and Integration Points
The header depends on bitops, limits, notifier blocks, printk, uapi watchdog definitions, sysfs attribute groups, devices, modules, and optional pretimeout governors. Integration points include char-device watchdog core, platform drivers, restart handlers, reboot notifiers, PM notifiers, and userspace watchdog daemons.

## Risks
Incorrect timeout validation can program hardware outside safe ranges. `nowayout` semantics must be honored. Drivers with a running hardware watchdog must ensure keepalive before registration completes. Stop-on-reboot/unregister flags affect system safety. Pretimeout must not race with final reset. Driver data should only be accessed through helpers.

## Test Signals
Signals include register/unregister, open/ping/close behavior, timeout and pretimeout ioctls, nowayout enforcement, reboot/restart handling, suspend/resume, managed registration cleanup, bootstatus reporting, and watchdog daemon integration.
