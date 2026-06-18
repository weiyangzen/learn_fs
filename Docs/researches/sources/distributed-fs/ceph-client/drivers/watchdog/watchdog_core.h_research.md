# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.h

## Purpose
`watchdog_core.h` is the private header shared by the watchdog core and watchdog character-device implementation. It defines the core-private device wrapper, maximum watchdog count, internal status bits, and internal function prototypes.

## Important APIs, types, and functions
`MAX_DOGS` limits registered watchdog devices to 32. `struct watchdog_core_data` contains the internal `struct device`, `struct cdev`, back-pointer to `struct watchdog_device`, mutex, keepalive timestamps, open deadline, hrtimer, kthread work, optional pretimeout hrtimer, and internal status bits `_WDOG_DEV_OPEN`, `_WDOG_ALLOW_RELEASE`, and `_WDOG_KEEPALIVE`. It declares `watchdog_dev_register()`, `watchdog_dev_unregister()`, `watchdog_dev_init()`, and `watchdog_dev_exit()`. It also defines `watchdog_have_pretimeout()` and hrtimer-pretimeout helper prototypes or no-op stubs.

## Control flow
The header has no standalone runtime flow, but its declarations define how `watchdog_core.c` delegates character-device registration to `watchdog_dev.c`, and how optional hrtimer pretimeout code is compiled in or compiled out.

## State and persistence behavior
The header defines volatile in-kernel state only. `watchdog_core_data` tracks open/keepalive timing and character device state while a watchdog is registered; it is not durable and is cleaned up on unregister.

## Dependencies and integration points
It depends on Linux cdev, device, hrtimer, kthread, mutex, init, and public watchdog types. It is private to the watchdog subsystem, not a driver-facing public API.

## Risks and test signals
Risks include ABI drift between `watchdog_core.c` and the character-device implementation, max-device assumptions from `MAX_DOGS`, and configuration-dependent pretimeout behavior. Test by building with and without `CONFIG_WATCHDOG_HRTIMER_PRETIMEOUT`, registering more than one watchdog, exercising open/magic-close/keepalive state transitions through `watchdog_dev.c`, and verifying internal status bits are not exposed as public ABI.
