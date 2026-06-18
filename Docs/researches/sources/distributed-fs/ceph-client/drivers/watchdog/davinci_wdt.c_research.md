# sources/distributed-fs/ceph-client/drivers/watchdog/davinci_wdt.c

## Purpose
`davinci_wdt.c` supports TI DaVinci/Keystone watchdog timers implemented as a 64-bit timer block with watchdog key sequencing. It is a nowayout watchdog with a restart callback.

## Important APIs, types, and functions
`struct davinci_wdt_device` stores the MMIO base, clock, and embedded watchdog. Core functions are `davinci_wdt_start`, `davinci_wdt_ping`, `davinci_wdt_get_timeleft`, and `davinci_wdt_restart`. Probe uses `devm_clk_get_enabled`, `devm_platform_ioremap_resource`, `watchdog_set_restart_priority`, and `devm_watchdog_register_device`.

## Control Flow
Start disables the timer, configures 64-bit watchdog mode, clears counters, writes PRD12/PRD34 from timeout and clock rate, enables periodic mode, then writes the WDKEY sequence to move pre-active to active. Ping repeats the service key sequence. Get-timeleft checks the timeout flag and subtracts elapsed counter seconds. Restart programs zero period, activates watchdog, then writes an invalid key value to trigger reset.

## State and Persistence
Runtime state is the clock, MMIO registers, timeout in watchdog core, and nowayout status hard-set to true. Once active, the watchdog registers become mostly write-protected except WDKEY fields.

## Dependencies and Integration Points
The driver depends on platform resources, OF compatible `ti,davinci-wdt`, the clock framework, MMIO accessors, watchdog core, and restart priority integration.

## Risks and Test Signals
Risks include 64-bit timeout multiplication, clock-rate changes, inability to stop once active, timeleft underflow if the counter exceeds timeout, and restart key sequencing. Tests should cover heartbeat module parameter validation, clock probe deferral, timeleft before/after timeout flag, ping sequence, restart assertion, and register programming under different clock rates.
