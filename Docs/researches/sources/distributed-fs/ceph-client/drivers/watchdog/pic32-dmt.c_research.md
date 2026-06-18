# sources/distributed-fs/ceph-client/drivers/watchdog/pic32-dmt.c

## Purpose
`pic32-dmt.c` drives the Microchip PIC32 Deadman Timer. It exposes a fixed hardware-programmed timeout and services the timer through a two-step clear sequence gated by the DMT window.

## Important APIs, types, and functions
`struct pic32_dmt` stores MMIO registers and clock. Helpers include `dmt_enable`, `dmt_disable`, `dmt_bad_status`, `dmt_keepalive`, `pic32_dmt_get_timeout_secs`, and `pic32_dmt_bootstatus`. Watchdog ops are `pic32_dmt_start`, `pic32_dmt_stop`, and `pic32_dmt_ping`.

## Control flow
Probe maps DMT registers, enables the clock, reads the timeout from the programmed postscaler count divided by clock rate, maps reset control temporarily to read/clear DMT reset cause, forces nowayout, and registers the global watchdog device. Start sets `DMT_ON` and performs the keepalive sequence. Keepalive writes pre-clear key, waits for `WINOPN`, writes the second key, and checks bad-event bits. Stop clears `DMT_ON` and issues a `nop` before further register access.

## State and persistence
The timeout is determined by hardware registers and is not settable by this driver. Reset cause in the PIC32 reset controller is read and cleared. The global watchdog object means one instance is assumed.

## Dependencies and integration points
It depends on OF compatible `microchip,pic32mzda-dmt`, PIC32 register set/clear address helpers from platform data, clock framework, watchdog core, and reset-controller base constants.

## Risks and test signals
Risks include fixed nowayout, global watchdog object across possible multiple devices, busy waiting for the DMT window without explicit error on timeout beyond bad-status check, and direct `ioremap` of reset base outside devm. Test signals include timeout readback, reset-cause clear, windowed keepalive success/failure, start/stop, clock failure, and nowayout behavior.
