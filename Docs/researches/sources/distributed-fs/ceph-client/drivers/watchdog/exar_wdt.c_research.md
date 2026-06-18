# sources/distributed-fs/ceph-client/drivers/watchdog/exar_wdt.c

## Purpose
This driver supports watchdog blocks in Exar/MaxLinear XR28V38x UART/Super-I/O devices. It scans Super-I/O configuration ports, creates platform devices for detected watchdogs, and exposes each through the watchdog core.

## Important APIs, types, and functions
`struct wdt_priv` contains I/O resource, config-port identity, runtime unit/timeout, spinlock, and watchdog device. Super-I/O helpers include `exar_sio_enter`, `exar_sio_read16`, `exar_sio_select_wdt`, and `exar_detect`. Watchdog operations are `exar_wdt_start`, `exar_wdt_stop`, `exar_wdt_keepalive`, and `exar_wdt_set_timeout`.

## Control Flow
Module init scans config ports `0x2e`/`0x4e` with multiple enter keys, validates vendor/device IDs, reads active runtime base, registers platform devices, then probes them. Probe initializes watchdog limits, configures the WDT control register, sets timeout, stops hardware, and registers. Start disarms, writes units, and arms by writing the timeout twice. Ping reads `WDT_VAL`; stop writes a safe disarm sequence.

## State and Persistence
State is per detected watchdog but platform-device nodes are tracked in a global list. Hardware state is in Super-I/O and runtime I/O registers. No persistent storage exists; detected platform devices are unregistered at module exit.

## Dependencies and Integration Points
The driver depends on raw I/O port access, muxed Super-I/O config regions, platform-device registration, list management, module timeout/nowayout, and watchdog core.

## Risks and Test Signals
Risks include false Super-I/O detection, I/O region conflicts, minute/second rounding above 255 seconds, multiple detected devices, and arm/disarm write sequencing. Tests should cover all enter keys, unsupported IDs, active flag false, multiple watchdog registration, timeout boundary at 255 seconds, and start/stop/ping I/O traces.
