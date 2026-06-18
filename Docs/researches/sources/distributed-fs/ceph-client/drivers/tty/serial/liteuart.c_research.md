# sources/distributed-fs/ceph-client/drivers/tty/serial/liteuart.c

## Purpose

`liteuart.c` is a serial-core driver for LiteX LiteUART controllers using 8-bit, 32-bit-aligned LiteX CSRs. It provides platform-device probing, optional IRQ operation, timer polling fallback, console support, and earlycon output.

## Important APIs, Types, and Functions

`struct liteuart_port` wraps `struct uart_port` with a polling `timer_list` and cached IRQ-enable register. `liteuart_driver` is the `uart_driver`, and `liteuart_ops` implements TX/RX, startup/shutdown, termios, config, and verify methods. Important helpers are `liteuart_update_irq_reg()`, `liteuart_rx_chars()`, `liteuart_tx_chars()`, `liteuart_interrupt()`, `liteuart_timer()`, `liteuart_probe()`, and console helpers `liteuart_console_write()` and `early_liteuart_setup()`.

## Control Flow

Probe maps the CSR region, optionally obtains an IRQ, allocates a line from DT alias or xarray, initializes the port, and calls `uart_add_one_port()`. Startup requests the IRQ when present; on request failure or no IRQ it sets `port->irq = 0` and starts a timer that repeatedly calls the same interrupt routine. RX drains until `OFF_RXEMPTY` is set, acknowledges RX pending to refresh the empty bit, and inserts normal chars because the hardware exposes no detailed error status. TX uses `uart_port_tx()` while `OFF_TXFULL` is clear. Shutdown disables event bits and frees either IRQ or timer.

## State and Persistence Behavior

Line ownership is stored in the static `liteuart_array` xarray. Per-port runtime state is the cached `irq_reg`, timer, and serial-core state. Hardware-visible state is event enable/pending and FIFO registers. There is no persistent configuration beyond the active port instance.

## Dependencies and Integration Points

The driver depends on LiteX CSR accessors (`litex_read8`/`litex_write8`), platform resources, OF aliases, xarray allocation, serial core, console core, and timer polling. Compatible string is `litex,liteuart`.

## Risks and Edge Cases

The CSR layout is explicitly limited to 8-bit CSR bus with 32-bit alignment. The timer path calls `liteuart_interrupt(0, port)`, passing a `uart_port *` where the IRQ handler expects a `struct liteuart_port *`; that path should be scrutinized because `to_liteuart_port()` is not applied there. Console write assumes a valid xarray entry. Error reporting is absent because hardware status lacks per-character error bits.

## Test Signals

Probe with DT aliases and auto allocation, IRQ and forced polling modes, TX/RX loopback, console and earlycon output, startup failure of IRQ request, timer shutdown, xarray cleanup on remove, and validation on nonstandard LiteX CSR layouts.
