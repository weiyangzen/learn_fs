# sources/distributed-fs/ceph-client/drivers/tty/serial/ip22zilog.c

## Purpose
`ip22zilog.c` is the serial-core driver for the Zilog SCC serial channels found on SGI IP22 systems. It exposes two channels as `ttyS` lines, supports optional console operation, observes IP22 register access timing delays, and maps SCC interrupt/status/data behavior into Linux UART operations.

## Important APIs, types, and functions
`struct uart_ip22zilog_port` wraps `struct uart_port` with `curregs` software shadow registers, TX/deferred-reload/reset/modem flags, break marker, parity mask, and previous status. Register access is via `read_zsreg()`, `write_zsreg()`, `ip22zilog_clear_fifo()`, `__load_zsregs()`, and `ip22zilog_maybe_update_regs()`. Interrupt work is split across `ip22zilog_interrupt()`, `ip22zilog_receive_chars()`, `ip22zilog_status_handle()`, and `ip22zilog_transmit_chars()`. Platform lifecycle is `ip22zilog_probe()`/`remove()` plus module init/exit.

## Control flow
Probe maps the SCC resource, prepares channel B as line 0 and channel A as line 1, requests the shared IRQ, and adds both UART ports. Startup resets the chip once, loads shadow registers, enables master interrupts, records initial status, enables RX/TX, and enables external/RX/TX interrupts. Termios updates compute a baud-rate-generator constant, update clock/width/parity/stop bits and status masks, and reload immediately or defer reload while TX is active. The IRQ handler reads channel A R3 pending bits, services both channels under locks, drains RX, handles status/break/modem events, advances TX, and pushes flip data after unlocking.

## State and persistence behavior
`curregs` is the authoritative shadow of SCC write registers. Reloads may be deferred with `IP22ZILOG_FLAG_REGS_HELD` until transmit completes. `prev_status` tracks modem and break edges; `tty_break` carries break/sysrq state to the following null character. State is volatile and hardware-local.

## Dependencies and integration points
The driver depends on SGI IP22 platform headers, platform resources, serial core, tty flip buffers, sysrq, optional console infrastructure, MMIO byte access, and constants from `ip22zilog.h`. It registers platform driver `ip22zilog` and UART driver `serial_ip22zilog`.

## Risks and test signals
Risks include timing-sensitive SCC register access, deferred register reload correctness, special console startup/shutdown rules, shared IRQ bookkeeping using `NULL` dev_id, and hand-maintained modem delta logic. Test both channels, console and non-console opens, active-TX termios changes, break/sysrq, modem waits, RX error classification, baud constants, and probe/remove on IP22 resources.
