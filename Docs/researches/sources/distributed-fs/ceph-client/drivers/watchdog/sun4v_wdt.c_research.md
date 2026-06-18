# sources/distributed-fs/ceph-client/drivers/watchdog/sun4v_wdt.c

## Purpose
`sun4v_wdt.c` implements a watchdog using SPARC sun4v hypervisor support. Instead of direct registers, it programs the machine watchdog through hypervisor calls and validates optional platform machine-description properties.

## Important APIs, types, and functions
Global `wdd` is the watchdog device. Watchdog ops are `sun4v_wdt_ping()` for start/ping, `sun4v_wdt_stop()`, and `sun4v_wdt_set_timeout()`. Initialization uses `mdesc_grab()`, `mdesc_node_by_name()`, `mdesc_get_property()`, `sun4v_hvapi_register()`, and watchdog registration.

## Control flow
Init obtains the machine description, finds the `platform` node, registers the core hypervisor API, validates `watchdog-resolution` and `watchdog-max-timeout`, adjusts `max_timeout` if needed, initializes timeout from module parameter, applies nowayout, and registers. Ping/start calls `sun4v_mach_set_watchdog(timeout * 1000, NULL)` and maps `HV_EINVAL` to `-EINVAL`. Stop programs zero. Exit unregisters hypervisor API and the watchdog.

## State and persistence behavior
State is mostly hypervisor-owned. The Linux driver stores configured timeout and max range, but countdown state persists in the hypervisor until reset, stop, or new timeout.

## Dependencies and integration points
It depends on SPARC hypervisor APIs, machine description access, module parameters, and watchdog core. It is platform-specific and returns `-ENODEV` or `-EINVAL` for missing/invalid hypervisor metadata.

## Risks and test signals
Risks include milliseconds/seconds conversion boundaries, hypervisor rounding to resolution, property validation rejecting systems, and leaving the hypervisor API registered on partial failures. Tests should cover absent platform node, invalid resolution/max-timeout properties, module timeout validation, HV_EINVAL mapping, stop programming zero, and exit unregister ordering.
