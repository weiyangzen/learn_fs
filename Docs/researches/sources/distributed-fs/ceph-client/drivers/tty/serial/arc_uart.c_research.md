# sources/distributed-fs/ceph-client/drivers/tty/serial/arc_uart.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/arc_uart.c` is the serial-core driver for Synopsys ARC on-chip FPGA UART hardware. It provides `ttyARC` ports, interrupt-driven RX/TX, console and earlycon support, and optional console polling for a small non-16550-compatible register set. The source was read as a complete 671-line file.

## Important APIs, Types, and Functions

The private object is `struct arc_uart_port`, wrapping `uart_port` plus the configured baud. Register macros describe 8-bit word-aligned registers `R_DATA`, `R_STS`, `R_BAUDL`, and `R_BAUDH`, with bits for RX/TX interrupt enable, FIFO empty/full, frame error, and overrun. Serial-core operations are `arc_serial_pops`, implemented by TX/RX start/stop, `arc_serial_tx_empty()`, `arc_serial_set_termios()`, modem stubs, break stub, startup/shutdown, config/verify, and poll helpers. Platform integration is through `arc_serial_probe()`, `arc_serial_init()`, and `arc_serial_exit()`.

## Control Flow

Module init registers the UART driver and then the platform driver. Probe requires an OF node, derives the line from the `serial` alias or defaults to zero, reads `clock-frequency` and `current-speed`, maps the MMIO resource, maps the IRQ, fills the static port entry, sets FIFO size to one for TX, initializes ignore masks, and adds the port.

Startup disables all UART interrupts, requests the shared RX/TX ISR, and enables only RX interrupts initially. The ISR reads status, handles RX when RX interrupts are enabled, and handles TX when TX interrupts are enabled and the TX register is empty. RX loops until `RXEMPTY`, clearing and accounting overrun/frame errors, reading chars, honoring sysrq, inserting into the TTY flip buffer, and pushing. TX is dynamic: start_tx writes one x_char or FIFO byte and enables TX interrupt if data was sent; TX ISR disables TX interrupts first, then calls the same TX helper, which reenables them only if more data was sent.

Termios obtains a baud from serial core, programs two baud registers using the ARC formula `CLK/(baud*4)-1`, disables all interrupts during programming, reenables RX interrupts, forces 8N1 and no hardware flow control/parity, copies old hardware settings when present, encodes baud back into termios, and updates the timeout.

## State and Persistence Behavior

State is static in `arc_uart_ports[]` and hardware registers. No persistent storage exists. The console path can be deferred until the backing port has a mapped `membase`. Earlycon programs baud registers from the early console baud and writes directly through the same polling putchar path.

## Dependencies and Integration Points

The driver depends on platform devices, OF address/IRQ helpers, serial core, TTY flip buffers, console/earlycon APIs, sysrq, and MMIO byte accessors. It matches `snps,arc-uart`.

## Risks and Edge Cases

`arc_serial_set_termios()` stores the requested baud in a local `baud` but calculates `hw_val` from `uart->baud`, which is initialized from the `current-speed` property; this means runtime baud changes deserve scrutiny. `arc_serial_poll_getchar()` loops while `!(status & RXEMPTY)`, which appears inverted for waiting on available data and could return stale/invalid data. The hardware has no real modem control, break generation, parity, or flow control. TX FIFO size is one, so interrupt pacing is sensitive to missed TX-empty events.

## Test Signals

Test signals include OF property validation, boot console and regular console handoff, RX/TX loopback, TX interrupt enable/disable sequencing, frame/overrun accounting, runtime termios baud changes, poll get/put behavior, multiport alias bounds, and startup/shutdown IRQ balancing.
