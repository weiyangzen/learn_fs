# sources/distributed-fs/ceph-client/drivers/watchdog/ftwdt010_wdt.c

## Purpose
This driver supports the Faraday FTWDT010 watchdog and compatible Cortina Gemini watchdog. It programs a fixed 5 MHz watchdog clock, optional pretimeout interrupt, and restart behavior.

## Important APIs, types, and functions
`struct ftwdt010_wdt` embeds the watchdog and stores device, MMIO base, and IRQ presence. `ftwdt010_enable` centralizes register programming. Watchdog ops are `ftwdt010_wdt_start`, `ftwdt010_wdt_stop`, `ftwdt010_wdt_ping`, `ftwdt010_wdt_set_timeout`, and `ftwdt010_wdt_restart`. `ftwdt010_wdt_interrupt` notifies watchdog pretimeout.

## Control Flow
Probe maps MMIO, initializes timeout limits and default 13 seconds, disables bootloader-enabled hardware, optionally requests an IRQ and marks pretimeout capability internally, and registers the watchdog. Start writes load value, restart magic, clock/reset mode, optional interrupt enable, and enable bit. Ping writes restart magic. Restart enables the watchdog with timeout zero. Suspend clears enable; resume re-enables only if watchdog core state is active.

## State and Persistence
Runtime state includes `has_irq`, watchdog timeout, and MMIO registers. Bootloader-enabled hardware is deliberately disabled at probe. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, optional IRQ, OF compatibles `faraday,ftwdt010` and `cortina,gemini-watchdog`, PM ops, and watchdog restart/pretimeout framework.

## Risks and Test Signals
Risks include hard-coded 5 MHz clock assumptions, disabling a bootloader watchdog without handoff, pretimeout notification without advertising `WDIOF_PRETIMEOUT`, and suspend disabling hardware. Tests should cover IRQ/no-IRQ modes, boot-enabled disable, timeout max calculation, restart path, suspend/resume active state, and register programming.
