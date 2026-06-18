# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.c

## Purpose
`watchdog_core.c` is the generic Linux watchdog registration core. It validates `struct watchdog_device` instances, assigns watchdog IDs, registers the character-device side through `watchdog_dev_register()`, supports deferred registration before misc/char infrastructure is ready, manages reboot/restart/PM notifiers, and provides managed registration helpers.

## Important APIs, types, and functions
Exported APIs are `watchdog_init_timeout()`, `watchdog_set_restart_priority()`, `watchdog_register_device()`, `watchdog_unregister_device()`, and `devm_watchdog_register_device()`. Internal functions include deferred-list helpers, `watchdog_check_min_max_timeout()`, `watchdog_reboot_notifier()`, `watchdog_restart_notifier()`, `watchdog_pm_notifier()`, `___watchdog_register_device()`, `__watchdog_register_device()`, `__watchdog_unregister_device()`, and init/exit routines.

## Control flow
`watchdog_init_timeout()` first validates a driver/module timeout, then `timeout-sec` firmware property, otherwise keeps the existing default and warns on invalid inputs. Registration is deferred until `watchdog_init()` has called `watchdog_dev_init()` and drained the deferred list. Real registration validates mandatory ops, allocates an ID from DT alias or an IDA, registers the char device, handles legacy watchdog0 conflicts by retrying a nonzero ID, applies global `stop_on_reboot`, registers reboot notifier, optional restart handler, and optional PM notifier. Unregister removes those hooks and frees the ID.

## State and persistence behavior
Core state includes `watchdog_ida`, deferred registration list and mutex, `wtd_deferred_reg_done`, and module parameter `stop_on_reboot`. Per-watchdog state is stored in each `watchdog_device` notifier blocks, status bits, ID, timeout, and core private data allocated by `watchdog_dev_register()`.

## Dependencies and integration points
The file depends on IDA allocation, device properties, OF aliases, reboot/restart/PM notifier APIs, tracepoints, `watchdog_dev_*` lower char-device helpers, and public watchdog status/ops contracts.

## Risks and test signals
Risks include ID leaks on complex failure paths, notifier registration inconsistencies, deferred unregister races, invalid driver ops accepted too early, and global `stop_on_reboot` overriding driver policy. Tests should cover timeout precedence and invalid fallback, deferred register/unregister before subsystem init, ID alias allocation and legacy watchdog0 retry, restart handler priority, reboot stop behavior with/without stop op, PM notifier paths, devm cleanup, and tracepoint coverage for stop failures.
