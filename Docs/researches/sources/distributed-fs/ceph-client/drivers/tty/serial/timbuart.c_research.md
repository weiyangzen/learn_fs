# sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.c

## Purpose

`timbuart.c` is the platform serial driver for the Timberdale FPGA UART. It registers one `ttyTU` UART port with Linux serial core, maps the Timberdale MMIO register block, handles shared IRQs by deferring RX/TX/modem work into a tasklet, and exposes the device as a `platform:timb-uart` driver. The file was read as a complete 496-line source file.

## Important APIs, Types, and Functions

The private `struct timbuart_port` wraps `struct uart_port` with a tasklet, DMA flag placeholder, last interrupt-enable snapshot, and platform device pointer. The `timbuart_ops` serial-core table implements `tx_empty`, modem-control methods, TX/RX start-stop, buffer flush, startup/shutdown, termios setup, resource request/release, and port verification. Notable helpers are `timbuart_handleinterrupt()`, `timbuart_tasklet()`, `timbuart_rx_chars()`, `timbuart_tx_chars()`, `timbuart_handle_rx_port()`, `timbuart_handle_tx_port()`, `timbuart_mctrl_check()`, and `timbuart_probe()/timbuart_remove()`.

## Control Flow

Probe allocates `struct timbuart_port`, initializes serial-core fields, discovers IORESOURCE_MEM and IRQ resources, sets up the tasklet, registers `timbuart_driver`, and adds the single port. Serial core later calls `timbuart_config_port()`, which requests and maps MMIO. On open, `timbuart_startup()` flushes RX, clears interrupt status, enables RX and CTS-delta interrupts, and requests the IRQ. The top-half interrupt checks `TIMBUART_IPR`, snapshots `IER`, disables interrupts, and schedules `timbuart_tasklet()`. The tasklet runs under `uart_port_lock()`, processes TX if DMA is not used, checks CTS changes, processes RX, then writes the newly composed interrupt-enable mask. TX is pull-based from the tty xmit FIFO and RX pushes characters into the tty flip buffer.

## State and Persistence Behavior

Persistent driver state is in the allocated `timbuart_port`, serial-core `uart_port`, tasklet, and the hardware registers. `last_ier` preserves pre-disable interrupt enables across the top half and tasklet. `port->icount`, `read_status_mask`, `ignore_status_mask`, modem state, and xmit FIFO state are owned by serial core. There is no file-backed persistence. Hardware state is reset or reprogrammed on startup, shutdown, flush, and termios changes.

## Dependencies and Integration Points

The driver depends on Linux platform devices, serial core, tty flip buffers, MMIO accessors, IRQ handling, tasklets, and register definitions from `timbuart.h`. It integrates with Timberdale platform-device enumeration via `.driver.name = "timb-uart"` and `MODULE_ALIAS("platform:timb-uart")`. The UART major/minor and register layout are local to the Timberdale UART interface.

## Risks and Edge Cases

`timbuart_tx_chars()` writes bytes but does not increment `port->icount.tx`, so diagnostics may under-report transmitted bytes. The type callback appears inverted, returning `"timbuart"` when `PORT_UNKNOWN`; that is unusual for serial-core type reporting. `timbuart_startup()` returns directly after `request_irq()` and does not undo enabled interrupts on IRQ failure. Probe registers the `uart_driver` per device even though `.nr = 1`, so multiple platform instances would conflict. RX error handling is minimal: full FIFO is counted as overrun and flushed, but individual parity/framing conditions are not represented. The `usedma` field is always zero here, so DMA paths are placeholders rather than implemented behavior.

## Test Signals

Useful validation includes boot/probe tests for `timb-uart`, `ttyTU0` creation, open/close cycles, IRQ handling under shared interrupts, TX/RX loopback or board-level data transfer, CTS-delta wakeups, termios baud selection across the supported `baudrates[]`, FIFO flush behavior, and module unload/reload. Kernel build coverage should include serial-core API compatibility and `PORT_TIMBUART` definitions.
