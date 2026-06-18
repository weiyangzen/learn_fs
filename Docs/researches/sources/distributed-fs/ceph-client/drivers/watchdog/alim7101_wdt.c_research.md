# sources/distributed-fs/ceph-client/drivers/watchdog/alim7101_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/alim7101_wdt.c` is a legacy miscdevice driver for the ALi M7101 PMU watchdog. Because the hardware watchdog timeout is very short, the driver maintains its own kernel timer to ping hardware about every quarter second while requiring userspace to refresh a longer software heartbeat. The complete 450-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `timeout`, `use_gpio`, and `nowayout`. Important state includes `timer`, `next_heartbeat`, `wdt_is_open`, `wdt_expect_close`, and `alim7101_pmu`. Hardware functions are `wdt_timer_ping()`, `wdt_change()`, `wdt_startup()`, `wdt_turnoff()`, and `wdt_keepalive()`. File operations are `fop_write()`, `fop_open()`, `fop_close()`, and `fop_ioctl()`. Lifecycle and system paths are `alim7101_wdt_init()`, `alim7101_wdt_unload()`, `wdt_notify_sys()`, and `wdt_restart_handle()`.

## Control Flow

Init finds the M7101 PMU and compatible M1533 south bridge, configures the PMU watchdog to a one-second timeout, handles old revision GPIO mode requirements, validates timeout, registers reboot and restart handlers, and registers `/dev/watchdog`. Open starts the watchdog and schedules the ping timer. Userspace writes extend `next_heartbeat` and optionally set magic close. The timer periodically re-arms the PMU only while `jiffies` is before `next_heartbeat`; otherwise it logs that the heartbeat was lost and stops pinging so hardware can reset. The restart handler enables the watchdog and spins until reset.

## State and Persistence Behavior

The driver maintains two layers of state: hardware is kept alive by the kernel timer, while userspace health is represented by `next_heartbeat`. Optional GPIO toggling supports old Cobalt hardware. Hardware configuration persists in PCI config bytes until changed or reset.

## Dependencies and Integration Points

It depends on PCI config access, timer APIs, reboot and restart notifier APIs, miscdevice `/dev/watchdog`, and watchdog ioctls. Kconfig `ALIM7101_WDT` depends on PCI and maps to `alim7101_wdt.o`.

## Risks and Edge Cases

The close path has a comment questioning whether the timer should be deleted on unexpected close; leaving it alive means hardware will continue to be serviced until the software heartbeat expires. Old revision detection can force `nowayout`. The restart handler busy-loops forever by design. Manual PCI probing and config writes are sensitive to revision checks and `use_gpio`.

## Test Signals

Check timer-driven ping cadence, heartbeat expiration reset path, magic close stop, nowayout on old hardware, timeout boundaries, GPIO mode transitions, reboot notifier shutdown, restart handler behavior, and failure unwind for notifier/misc registration.
