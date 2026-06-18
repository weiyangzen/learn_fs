# sources/distributed-fs/ceph-client/drivers/tty/serial/st-asc.c

## Purpose

`st-asc.c` is the STMicroelectronics Asynchronous Serial Controller driver. It registers up to eight `ttyAS` ports, supports memory-mapped ASC FIFOs, configurable baud modes, parity/stop/data-length handling, optional hardware CTS/RTS flow control, manual RTS through GPIO and pinctrl state switching, console, console polling, wakeup signaling on RX, and suspend/resume through serial core. The source was read as a complete 976-line file.

## Important APIs, Types, and Functions

The hardware contract is described by `ASC_*` offsets and masks for baud rate, TX/RX buffers, control, interrupt enable, status, timeout, resets, retries, RX error bits, FIFO status, and control modes. `struct asc_port` embeds `struct uart_port` and stores an optional RTS GPIO, clock, pinctrl handle, default/no-hardware-flow-control states, and booleans for hardware flow control and forced baud mode 1.

Low-level helpers are `asc_in()`, `asc_out()`, interrupt enable/disable helpers, FIFO status helpers, `asc_hw_txroom()`, `asc_transmit_chars()`, and `asc_receive_chars()`. UART operations are in `asc_uart_ops`: TX/RX control, modem control, startup/shutdown, PM, termios, config/type/verify, and optional poll operations. Platform setup flows through `asc_of_get_asc_port()`, `asc_init_port()`, `asc_serial_probe()`, and `asc_serial_remove()`. Console support is implemented by `asc_console_putchar()`, `asc_console_write()`, and `asc_console_setup()`.

## Control Flow

Module init registers the UART driver and platform driver. Probe resolves the port slot from `serial` or `ttyAS` aliases, records DT booleans (`uart-has-rtscts`, `st,force-m1`), maps MMIO, gets IRQ and clock, briefly enables the clock to read `uartclk`, initializes pinctrl states, and adds the port. Startup requests the IRQ, primes TX, and enables RX interrupts. The IRQ handler locks the port, reads status, receives while RX buffer full, transmits when TX FIFO is at least half empty and TX interrupts are enabled, then unlocks.

RX reads `ASC_STA` and `ASC_RXBUF`, synthesizes dummy status bits for normal RX, break, and overrun, optionally ignores parity in 8-bit modes because the datasheet marks PE undefined, handles wakeup events when the IRQ is configured as wake-capable, updates `icount`, calls break/sysrq helpers, inserts chars with the correct tty flag, and pushes the flip buffer. TX uses `uart_port_tx_limited()` with space computed from empty/half-empty/not-full status. Termios stops the controller, resets FIFOs, coerces unsupported CMSPAR and unavailable CRTSCTS, selects 7-bit-with-parity or 8-bit modes, sets stop/parity, toggles CTS hardware flow control, programs either simple divisor mode for low baud or mode 1 fractional-style baud for higher rates or `st,force-m1`, updates masks and timeout, restarts the controller, and outside the port lock switches pinctrl/GPIO RTS ownership if flow-control mode changed.

## State and Persistence Behavior

Static state is `asc_ports[ASC_MAX_PORTS]` plus `asc_uart_driver`. Each `asc_port` persists for its platform device and stores clock, pinctrl states, RTS GPIO ownership, line number, and DT booleans. Live controller state is in ASC control/baud/FIFO/interrupt registers and is reprogrammed by termios and PM. PM `UART_PM_STATE_OFF` clears `ASC_CTL_RUN` under the port lock and disables the clock; PM on enables the clock. There is no file-backed persistence.

## Dependencies and Integration Points

The driver integrates with serial core, tty flip buffers, console and console-poll, platform/OF matching (`st,asc`), clock framework, pinctrl, GPIO descriptors, IRQ wakeup metadata, and PM helpers. It uses `uart_get_baud_rate()`, `uart_update_timeout()`, `uart_handle_break()`, `uart_handle_sysrq_char()`, `uart_insert_char()`, `uart_console_write()`, and `uart_suspend_port()`/`uart_resume_port()`.

## Risks and Edge Cases

Manual RTS switching is delicate: when hardware flow control is disabled and the optional `no-hw-flowctrl` pinctrl state exists, the driver obtains an RTS GPIO with devm during termios; when hardware flow control is reenabled, it releases the GPIO and restores the default pinctrl state. `manual_rts` is only assigned inside the branches that set `toggle_rts`, so future edits must preserve that invariant. Console writes disable all ASC interrupts and busy-wait up to 1 second for FIFO empty/space. The driver has no early console and expects console setup only after probe/mapping. `asc_startup()` calls `asc_transmit_chars()` before RX interrupt enable, which depends on valid tty state. `asc_receive_chars()` dereferences `tport->tty->dev` for wakeup events when IRQ wake is set, so wake configuration should only occur when tty state is valid.

## Test Signals

Important signals include OF probe with `serial` and `ttyAS` aliases, missing/invalid pinctrl states, `uart-has-rtscts` and `st,force-m1` combinations, termios transitions between hardware flow control and manual RTS GPIO, baud programming below and above 19200, 7-bit/parity and 8-bit modes with parity-error behavior, RX break/frame/parity/overrun injection, wakeup IRQ RX activity, console and poll I/O, suspend/resume clock and `ASC_CTL_RUN` handling, module unload, and repeated open/close IRQ lifetime checks.
