# sources/distributed-fs/ceph-client/drivers/tty/serial/meson_uart.c

## Purpose

`meson_uart.c` is the Amlogic Meson UART driver. It supports multiple compatibles, two possible TTY driver names (`ttyAML` and `ttyS`), console/earlycon and polling-console support, clock-based baud programming, optional hardware flow control, and dynamic registration/unregistration of the relevant UART driver.

## Important APIs, Types, and Functions

`struct meson_uart_data` selects the UART driver and XTAL divider behavior. Static `meson_ports[AML_UART_PORT_NUM]` tracks active ports. `meson_uart_ops` provides serial-core callbacks plus optional `poll_get_char`/`poll_put_char`. Key routines are `meson_uart_start_tx()`, `meson_receive_chars()`, `meson_uart_interrupt()`, `meson_uart_reset()`, `meson_uart_startup()`, `meson_uart_change_speed()`, `meson_uart_set_termios()`, `meson_uart_probe_clocks()`, `meson_uart_probe()`, and console/earlycon helpers.

## Control Flow

Probe derives the line from DT alias or an offset auto-allocation range, obtains resources/IRQ/fifo size/flow-control property, enables pclk/xtal/baud clocks, registers the selected UART driver if needed, initializes the port, briefly maps/resets/releases hardware before `uart_add_one_port()`, and stores it in `meson_ports`. Startup clears errors, enables RX/TX and both IRQs, configures FIFO IRQ trigger levels, and requests IRQ. IRQ handling drains RX when non-empty and starts TX when TX FIFO is not full and TX interrupts are enabled. Termios updates format, parity, stop bits, two-wire/RTSCTS mode, baud, and status masks.

## State and Persistence Behavior

State persists in `meson_ports`, serial-core port objects, clock-enabled resources managed by devm, and hardware control/status registers. Removal unregisters the selected UART driver only when no ports remain. No explicit suspend/resume state appears in this file.

## Dependencies and Integration Points

Dependencies include platform/OF, common clock framework, serial core, console and earlycon, console polling for KGDB-style use, MMIO, and compatible-specific data for G12A/A1/S4. Earlycon supports `amlogic,meson-ao-uart` and `amlogic,meson-s4-uart`.

## Risks and Edge Cases

The RX error path increments `icount.frame` for parity errors, which should be checked against intended accounting. Dynamic UART driver unregister only considers the current driver pointer; mixed `ttyAML` and `ttyS` devices need careful remove ordering. Probe reset maps and releases before normal serial-core request, so mapping lifecycle must remain matched. Hardware flow is disabled in termios if the DT property did not set `UPF_HARD_FLOW`.

## Test Signals

Compatibles selecting `ttyAML` versus `ttyS`, alias and auto line assignment, console/earlycon/polling I/O, XTAL div2 baud programming, RTSCTS property behavior, RX break/parity/frame/overrun handling, TX interrupt enable/disable, mixed port removal, and clock failure paths.
