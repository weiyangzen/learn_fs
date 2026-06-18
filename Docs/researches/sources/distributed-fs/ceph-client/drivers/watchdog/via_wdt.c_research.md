# sources/distributed-fs/ceph-client/drivers/watchdog/via_wdt.c

## Purpose
`via_wdt.c` drives watchdog hardware in VIA chipsets. It allocates/configures a small MMIO window through PCI config space, registers a watchdog, and uses an internal timer to ping the hardware at 500 ms intervals while userspace heartbeat has not expired.

## Important APIs, types, and functions
Global state includes `wdt_dev`, allocated `wdt_res`, mapped `wdt_mem`, `mmio`, timer `timer`, and `next_heartbeat`. Watchdog ops are `wdt_start()`, `wdt_stop()`, `wdt_ping()`, and `wdt_set_timeout()`. Hardware helpers include `wdt_reset()` and timer callback `wdt_timer_tick()`. PCI entry points are `wdt_probe()` and `wdt_remove()`.

## Control flow
Probe enables the PCI device, allocates an MMIO address, writes it to PCI config, enables watchdog/MMIO decode, reserves and maps the region, initializes timeout and bootstatus, registers the watchdog, then starts the internal ping timer in case BIOS had already enabled hardware. Start writes timeout count, sets running and trigger bits, updates `next_heartbeat`, and arms the timer. The timer keeps resetting hardware while userspace deadline has not passed or the watchdog is inactive; otherwise it stops pinging and logs impending reboot.

## State and persistence behavior
Software heartbeat deadline is separate from the hardware one-second heartbeat. Hardware fired/running/count/control bits persist in the chipset. Removing the driver unregisters, deletes the timer, unmaps, releases resources, and disables PCI device.

## Dependencies and integration points
It depends on VIA PCI IDs, PCI config access, global I/O memory resource allocation, timers/jiffies, MMIO, and watchdog core.

## Risks and test signals
Risks include BIOS/PnP MMIO setup failure, global singleton state, timer continuing around removal if not synchronized, and heartbeat policy split between userspace and internal timer. Tests should cover MMIO allocation/config verification, bootstatus fired bit, internal timer behavior before/after user heartbeat expiry, timeout count writes, stop clearing running bit, and resource cleanup.
