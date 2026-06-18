# sources/distributed-fs/ceph-client/drivers/tty/serial/sunplus-uart.c

## Purpose
This is the Sunplus SP7021 UART platform driver. It is 8250-like but not register-compatible, so it implements its own register access, IRQ handling, console, earlycon, clock/reset management, and uart-core operations.

## Important APIs, Types, And Functions
`struct sunplus_uart_port` embeds `uart_port` and stores clock/reset handles. `sunplus_uart_ops` covers mctrl, tx/rx start/stop, break, startup/shutdown, termios, line discipline PPS handling, type/config/verify, and optional console polling.

`transmit_chars()` drains the tty xmit FIFO while the TX FIFO is not full. `receive_chars()` loops while RX data is present, updates icount for break/parity/frame/overrun, handles sysrq, honors CREAD via `SUP_DUMMY_READ`, inserts tty chars, and pushes flip buffers. `sunplus_uart_irq()` reads the interrupt status/control register and dispatches RX/TX handling.

Probe obtains `serial` alias id, allocates state, enables the optional clock, deasserts reset, maps registers, sets port fields, stores console port state when enabled, and calls `uart_add_one_port()`.

## Control Flow
Module init registers the uart driver and platform driver. `startup()` requests the IRQ and enables RX interrupts. TX interrupts are enabled only by `start_tx()` and disabled when the FIFO empties. `shutdown()` writes zero to the interrupt control register and frees the IRQ. `set_termios()` computes Sunplus's split divisor/ext divisor format, configures data bits/parity/stop bits, updates timeout and status masks, optionally flushes RX when CREAD is clear, then writes divisor and LCR registers.

## State And Persistence
Runtime state lives in the per-device `sunplus_uart_port`, register bits, and serial-core counters/masks. Console builds a static `sunplus_console_ports[SUP_UART_NR]` lookup. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on platform/OF, `serial` aliases, clock framework, reset controller, serial core, tty flip buffers, console/earlycon, sysrq, and generic 8250 bit definitions from `serial_reg.h`. It matches `sunplus,sp7021-uart` and exposes `ttySUP`.

## Risks
`sunplus_tx_empty()` checks `UART_LSR_TEMT` against the Sunplus LSR layout even though TX-not-full is bit 0; this depends on hardware exposing a compatible TEMT bit or may underreport empty state. Interrupt status bits are read-to-clear while enable bits share the same register, so careless read/modify/write ordering can drop status or mask interrupts. The driver maps modem outputs through MCR bits, but external modem behavior depends on hardware wiring. Suspend skips console ports, so non-console-only PM coverage is needed.

## Test Signals
Tests should cover probe/remove, alias id bounds, clock/reset failure unwind, RX/TX interrupt operation, break/parity/frame/overrun status accounting, CREAD clearing and RX flush, termios divisor accuracy, PPS line discipline flag toggling, console/earlycon writes, suspend/resume, and TX empty behavior on real hardware.
