# sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon.c

## Purpose
Driver for the Broadcom SSB ChipCommon core, covering clock/power setup, PMU handoff, watchdog access, flash/external bus timings, GPIO register helpers, IRQ status/mask helpers, and optional UART discovery.

## Important APIs, Types, and Functions
Public functions include `ssb_chipcommon_init/suspend/resume`, `ssb_chipco_set_clockmode`, clock getters, timing init, watchdog setters, IRQ helpers, GPIO helpers (`ssb_chipco_gpio_*`), and optional `ssb_chipco_serial_init`. Internal helpers derive slow clock source/frequency limits, power-control delays, watchdog limits, and masked register writes under `gpio_lock`.

## Control Flow
Init validates ChipCommon presence, initializes GPIO lock, reads status for rev >=11, clears pullup/pulldown for rev >=20, initializes PMU if present, sets power-control timing, forces fast clock mode, calculates PCI fast powerup delay, and computes watchdog timing for SoC buses. Suspend sets slow clock mode; resume re-runs power control and fast mode. GPIO helpers perform masked read-modify-write with spinlocks. Serial init chooses baud source based on PLL type/revision, optionally toggles UART clocks, and fills port descriptors.

## State and Persistence
Updates `struct ssb_chipcommon` fields such as `status`, `fast_pwrup_delay`, `ticks_per_ms`, and `max_timer_ms`. Hardware state persists in ChipCommon clock, GPIO, watchdog, PMU, and timing registers.

## Dependencies and Integration Points
Used by SSB main bus power management, MIPS core flash/serial setup, GPIO driver, embedded watchdog registration, PMU code, and PCI xtal control. Depends on `ssb_read/write`, PCI config access for old clock source detection, and BCM47xx watchdog definitions.

## Risks
Clock mode handling is revision-sensitive and PMU-capable chips bypass legacy control. Wrong timing calculations can break flash, UART, or external I/O. Watchdog width differs by revision/PMU and clamps requested ticks. GPIO RMW must stay locked to avoid lost updates.

## Test Signals
Boot logs should show ChipCommon status and PMU detection where present. Validate clock speed, UART baud, watchdog max, GPIO direction/value/pull behavior, and suspend/resume without losing bus access.
