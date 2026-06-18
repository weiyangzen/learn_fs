# sources/distributed-fs/ceph-client/drivers/watchdog/ep93xx_wdt.c

## Purpose
`ep93xx_wdt.c` supports the Cirrus Logic EP93xx watchdog, whose hardware timeout is about 250 ms. The driver relies on the watchdog core to provide a longer software timeout via frequent hardware heartbeats.

## Important APIs, types, and functions
`struct ep93xx_wdt_priv` stores MMIO base and embedded watchdog. Operations are `ep93xx_wdt_start`, `ep93xx_wdt_stop`, and `ep93xx_wdt_ping`, which write magic values to `EP93XX_WATCHDOG`. Probe reads status, initializes `max_hw_heartbeat_ms = 200`, and registers through `devm_watchdog_register_device`.

## Control Flow
Probe maps MMIO, reads the watchdog register for bootstatus and nCS1-disable status, initializes timeout limits, applies module timeout/nowayout, and registers the device. Start writes `0xaaaa`, stop writes `0xaa55`, and ping writes `0x5555`. The core keeps pinging within the short hardware heartbeat window while honoring the user timeout.

## State and Persistence
Runtime state is private MMIO pointer and watchdog core settings. Bootstatus is derived from a hardware bit read at probe. Hardware state is otherwise volatile.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, EP93xx platform device naming, watchdog core software heartbeat support, and module parameters.

## Risks and Test Signals
Risks include missing `.set_timeout` despite advertising `WDIOF_SETTIMEOUT`, very short hardware heartbeat pressure, bootstatus interpretation, and stop behavior under nowayout. Tests should cover software timeout feeding, start/stop/ping magic writes, bootstatus bit, module timeout initialization, and registration failure paths.
