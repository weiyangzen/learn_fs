# sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.c` is a watchdog-core driver for Atmel AT91SAM9x and AT91CAP9 watchdog hardware. The hardware mode register can be written only once, and the hardware cannot really be stopped, so the driver uses a kernel timer to keep the hardware alive while watchdog-core active state represents userspace health. The complete 405-line source was read for this report.

## Important APIs, Types, and Functions

`struct at91wdt` stores watchdog device, MMIO base, next userspace heartbeat, kernel ping timer, desired/current mode bits, heartbeat interval, nowayout flag, IRQ, and slow clock. Helpers include `at91_wdt_reset()`, `at91_ping()`, `at91_wdt_start()`, `at91_wdt_stop()`, `at91_wdt_set_timeout()`, `at91_wdt_init()`, `of_at91wdt_init()`, `wdt_interrupt()`, `at91wdt_probe()`, and `at91wdt_remove()`.

## Control Flow

Probe builds default mode bits, maps registers, enables the slow clock, parses DT properties, and calls `at91_wdt_init()`. Init reads the hardware mode register, writes it only if still reset-default, rejects disabled hardware when Linux expects enabled watchdog, computes safe min/max ping intervals from watchdog value and delta window, optionally requests an IRQ for software watchdog mode, sets up a timer, starts periodic pinging quickly, initializes watchdog timeout from DT or module parameter, and registers the watchdog. `start()` updates `next_heartbeat`; `stop()` is a no-op because hardware cannot stop. The timer keeps pinging while userspace heartbeat is valid or watchdog is not active; otherwise it stops pinging and lets hardware reset.

## State and Persistence Behavior

The driver maintains a distinction between hardware liveness and userspace liveness. Hardware is continuously refreshed by `timer` unless userspace expires. `mr` and `mr_mask` record desired mode-register state, while the actual hardware register may already be fixed by boot firmware. Removal unregisters and deletes the timer but warns that hardware will probably reboot.

## Dependencies and Integration Points

It depends on `at91sam9_wdt.h` register definitions, OF properties such as `atmel,max-heartbeat-sec`, `atmel,min-heartbeat-sec`, `atmel,watchdog-type`, `atmel,reset-type`, `atmel,disable`, `atmel,idle-halt`, and `atmel,dbg-halt`, optional IRQ, slow clock, MMIO access, timers, and watchdog core.

## Risks and Edge Cases

Mode-register one-write semantics are high risk: bootloader configuration may be immutable and incompatible. Windowed watchdog timing can be too tight for Linux scheduling, producing warnings or rejection. `stop()` cannot stop hardware, so users may misunderstand close semantics. Software reset mode calls `emergency_restart()` from IRQ context.

## Test Signals

Test default and DT mode register construction, already-configured hardware warnings, disabled-watchdog rejection, min/max heartbeat calculations, IRQ software mode, timer ping cadence, userspace heartbeat expiration, remove behavior, and watchdog timeout initialization from DT/module parameters.
