# sources/distributed-fs/ceph-client/drivers/watchdog/orion_wdt.c

## Purpose
`orion_wdt.c` supports Marvell Orion, Kirkwood, Dove, Armada 370/375/380/XP watchdogs. It abstracts SoC-specific clock, counter, reset-output, mask, and optional pretimeout behavior behind a shared watchdog core device.

## Important APIs, types, and functions
`struct orion_watchdog_data` provides offsets, enable bits, and SoC-specific callbacks. `struct orion_watchdog` stores watchdog object, timer/reset MMIO, clock, rate, and match data. Important functions are clock init variants, start/stop variants, `orion_wdt_ping`, `orion_wdt_enabled`, `orion_wdt_get_regs`, `orion_wdt_probe`, `orion_wdt_irq`, and `orion_wdt_pre_irq`.

## Control flow
Probe selects match data, maps timer and reset-output registers with backward-compatible fallback for legacy DTs, initializes the clock/rate, computes max timeout from 32-bit cycle count, normalizes module heartbeat, stops hardware unless already enabled, requests optional reset/panic IRQ and optional pretimeout IRQ, applies nowayout, and registers. Start delegates to the SoC variant to write counter, clear status, enable timer and reset output/mask. Ping reloads watchdog and optional timer1 pretimeout counter. Stop disables reset output and timer bits per variant.

## State and persistence
State is in timer counter/control/status registers, reset output registers, optional reset-output mask, clock enable state, and global `orion_wdt_info.options` when pretimeout IRQ exists. Hardware may be inherited running from bootloader and marked `WDOG_HW_RUNNING`.

## Dependencies and integration points
It depends on OF match data for Marvell compatibles, platform MMIO resources, clock framework including named fixed clocks, optional IRQs, watchdog pretimeout notification, and restart/reset output hardware.

## Risks and test signals
Risks include legacy hardcoded RSTOUT fallback, shared mutable `orion_wdt_info` causing pretimeout option leakage across devices, overflow in `clk_rate * timeout` writes, clock cleanup on probe failure, and optional IRQ semantics where primary IRQ panics. Test signals include every compatible mapping, missing second/third resources, fixed-clock fallback, running-at-boot detection, pretimeout IRQ, timeout maximum math, and shutdown stop behavior.
