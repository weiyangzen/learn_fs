# sources/distributed-fs/ceph-client/drivers/tty/serial/sunzilog.c

## Purpose
This driver supports Zilog Z8530/ESCC serial chips on Sun SPARC systems. Each chip has channel A and channel B, used either as tty serial ports or as keyboard/mouse serio devices.

## Important APIs, Types, And Functions
`struct uart_sunzilog_port` embeds `uart_port`, links into an IRQ-service chain, caches all Zilog write registers in `curregs`, stores flags for console, keyboard, mouse, KGDB, modem status, channel A, deferred register update, TX stopped/active, ESCC, and ISR availability, plus parity mask, previous status, and optional serio state.

`read_zsreg()`/`write_zsreg()` implement indexed register access with platform-specific delay/write-sync rules. `__load_zsregs()` programs the channel safely, detects ESCC extensions, resets errors/FIFOs/status, and loads baud/format/interrupt registers. `sunzilog_maybe_update_regs()` defers full register reloads while TX is active. RX, status, and TX interrupt paths are `sunzilog_receive_chars()`, `sunzilog_status_handle()`, and `sunzilog_transmit_chars()`.

## Control Flow
Init counts `zs` nodes, allocates channel and chip-register tables, registers minors for non-keyboard/mouse chips, registers the platform driver, then requests a shared IRQ after probes establish `zilog_irq`. Probe maps the chip, initializes both channels, registers tty ports for serial chips, or prints/registers serio devices for keyboard/mouse chips. The shared ISR walks the linked channel chain, reads channel A pending bits from R3, handles A events, then advances to channel B and handles B events.

Termios changes compute BRG constants and update cached registers for word size, stop bits, parity, masks, modem status interest, timeout, and deferred hardware reload. Console setup reads firmware termios, configures break interrupts, sets mctrl, and starts the channel without depending on normal startup.

## State And Persistence
State persists in `sunzilog_port_table`, `sunzilog_chip_regs`, `sunzilog_irq_chain`, `zilog_irq`, and per-port cached registers. The cached-register model is important because many changes must wait until transmit is no longer active. No disk persistence exists.

## Dependencies And Integration Points
The file depends on OF/platform resources, SPARC IRQ setup, serial core, console/sysrq, tty flip buffers, optional serio, `suncore` helpers, and `sunzilog.h` register definitions. It exposes `ttyS` lines and optional `zskbd`/`zsms` serio devices.

## Risks
Indexed Zilog register access is timing-sensitive, especially on 32-bit SPARC where delays are required. The IRQ handler assumes channel pairs and `next` links are valid; table allocation and probe ordering must match counted nodes. There is a probable bug pattern where console matching for channel B sets `up->flags` instead of `up[1].flags`. Modem delta detection uses manual previous-status tracking and must be verified. Deferred register reloads are required to avoid corrupting TX.

## Test Signals
Test serial and keyboard/mouse `zs` nodes, shared IRQ handling for both channels, ESCC detection and FIFO bits, console firmware termios, break/sysrq and `sun_do_break()`, deferred termios changes during active TX, modem status deltas, poll console operations, serio registration/open/write, and module exit disabling MIE/freeing IRQ.
