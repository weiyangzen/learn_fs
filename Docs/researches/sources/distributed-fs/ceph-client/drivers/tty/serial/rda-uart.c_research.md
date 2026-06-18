# sources/distributed-fs/ceph-client/drivers/tty/serial/rda-uart.c

## Purpose

`rda-uart.c` implements the serial-core driver for the RDA8810PL UART block. It provides up to three `ttyRDA` ports, supports platform/OF probing, interrupt-driven PIO transmit and receive, modem-control bits for RTS/CTS/loopback, regular console support, and OF early console support for `rda,8810pl-uart`.

## Important APIs, Types, and Functions

`struct rda_uart_port` wraps `uart_port` with the controller clock. The global `rda_uart_ports[]` array backs console lookup by line. `rda_uart_read()` and `rda_uart_write()` are the MMIO helpers. The `uart_ops` table maps serial core callbacks to `rda_uart_tx_empty()`, modem control helpers, TX/RX start/stop, startup/shutdown, termios programming, request/release/config/verify hooks, and type reporting.

`rda_uart_set_termios()` is the main configuration routine. It chooses a supported baud, sets the input clock to `baud * 8`, programs 7- or 8-bit characters, stop bits, parity including mark/space, hardware flow control, trigger levels, interrupt masks, and timeout state. `rda_uart_send_chars()` drains x_char and the tty xmit FIFO into the TX register while room remains. `rda_uart_receive_chars()` drains the RX FIFO and maps parity, framing, and overrun bits into tty flags and counters. `rda_interrupt()` acknowledges IRQ cause bits and dispatches RX or TX work.

## Control Flow

Probe obtains the OF serial alias as `pdev->id`, validates it against the three-port limit, maps the MMIO resource through the serial-core request path, obtains the IRQ and clock, initializes the `uart_port`, stores the port in `rda_uart_ports[]`, and calls `uart_add_one_port()`. Startup masks all interrupts, requests the IRQ with `IRQF_NO_SUSPEND`, enables the UART, and enables RX-data and RX-timeout interrupts. TX starts by enabling the TX-data-needed interrupt; the ISR then disables that interrupt while it fills the FIFO and re-enables it if more data remains. RX starts from RX data/timeout IRQs and drains until the RX FIFO count is zero. Shutdown stops TX/RX, disables the UART, and leaves IRQ release to serial core shutdown teardown through the requested IRQ path.

## State and Persistence Behavior

The driver has no persistent storage. Runtime state is per-port MMIO state, the selected clock rate, the global console lookup array, tty counters, xmit FIFO contents owned by serial core, and IRQ mask bits. Hardware FIFO contents and control/trigger settings persist while the UART block remains powered. Console writes temporarily mask interrupts, poll for TX room, write characters, wait for completion, and restore the previous IRQ mask.

## Dependencies and Integration Points

The file depends on platform device resources, OF aliases and compatible matching, clocks, MMIO, IRQs, serial core, tty flip buffers, console and earlycon infrastructure. It integrates with `uart_register_driver()`/`platform_driver_register()` at module init and with the console layer through `rda_uart_console` and `OF_EARLYCON_DECLARE()`.

## Risks and Edge Cases

`rda_uart_tx_empty()` appears to return `TIOCSER_TEMT` when the TX FIFO mask is nonzero, which is counterintuitive if the mask encodes occupancy rather than available space; this should be validated against hardware documentation. TX and console paths busy-wait with `cpu_relax()` and no timeout if the TX FIFO never becomes writable. `rda_uart_stop_rx()` reads one RXTX word before resetting RX FIFO to avoid timeout, which may discard a byte. DMA bits are deliberately cleared even though the register definitions expose DMA completion IRQs. Unsupported CS5/CS6 is coerced to CS7, and no runtime PM or clock prepare/enable calls are present beyond using the clock for rate control.

## Test Signals

Test DT alias bounds, missing clock or zero clock rate, IRQ request failure, 7-bit and 8-bit termios, parity variants, two stop bits, CRTSCTS and manual RTS, loopback, RX timeout and RX data IRQs, parity/frame/overrun flags, TX x_char priority, FIFO reset on stop, console write with active interrupts, early console output, and behavior when TX-ready polling never completes.
