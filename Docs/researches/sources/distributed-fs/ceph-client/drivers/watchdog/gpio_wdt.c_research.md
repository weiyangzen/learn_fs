# sources/distributed-fs/ceph-client/drivers/watchdog/gpio_wdt.c

## Purpose
`gpio_wdt.c` implements a generic external watchdog controlled by a GPIO line. It supports toggle-style and pulse/level-style hardware algorithms and can model always-running hardware.

## Important APIs, types, and functions
`struct gpio_wdt_priv` stores the GPIO descriptor, current toggle state, always-running flag, algorithm selector, and embedded watchdog. Operations are `gpio_wdt_start`, `gpio_wdt_stop`, and `gpio_wdt_ping`; `gpio_wdt_disable` holds or tristates the line depending on algorithm.

## Control Flow
Probe reads required `hw_algo` and `hw_margin_ms` properties, obtains the GPIO with suitable direction, reads optional `always-running`, initializes watchdog limits, and registers. Toggle mode starts as output low and flips the state on each ping. Level mode pulses high for one microsecond then low. Stop disables the GPIO only when hardware is not always running; otherwise it sets `WDOG_HW_RUNNING` so the core continues feeding.

## State and Persistence
Runtime state includes GPIO direction/value, last toggle state, and watchdog core status. External hardware may remain running independently of driver lifetime, especially with `always-running`.

## Dependencies and Integration Points
The driver depends on firmware properties, GPIO descriptor APIs, optional arch initcall registration, OF compatible `linux,wdt-gpio`, and watchdog core software heartbeat via `max_hw_heartbeat_ms`.

## Risks and Test Signals
Risks include wrong algorithm property, invalid heartbeat margin, GPIO polarity assumptions, stop semantics for always-running devices, and one-microsecond pulse timing. Tests should cover toggle and level modes, missing/invalid properties, always-running start/stop, GPIO probe deferral, max heartbeat feeding, and reboot stop behavior.
