# sources/distributed-fs/ceph-client/drivers/tty/serial/lpc32xx_hs.c

## Purpose

`lpc32xx_hs.c` drives the high-speed UART blocks on NXP LPC32xx SoCs. It provides a fixed-size platform UART set, MMIO FIFO/interrupt handling, baud-divider calculation from the main oscillator, console support, and basic PM suspend/resume through serial core.

## Important APIs, Types, and Functions

`struct lpc32xx_hsuart_port` wraps `struct uart_port`; static `lpc32xx_hs_ports[MAX_PORTS]` holds up to three ports. `serial_lpc32xx_pops` implements the serial-core operations. Key functions are `__serial_get_clock_div()`, `__serial_uart_flush()`, `__serial_lpc32xx_rx()`, `__serial_lpc32xx_tx()`, `serial_lpc32xx_interrupt()`, `serial_lpc32xx_startup()`, `serial_lpc32xx_shutdown()`, `serial_lpc32xx_set_termios()`, `serial_hs_lpc32xx_probe()`, and console wait/write/setup helpers.

## Control Flow

Probe selects the next static port slot, stores mapbase and IRQ, initializes `uart_port`, puts the hardware into loopback mode by default, and registers the port. Startup flushes the FIFO, clears latched TX/error/break/overrun interrupts, programs default timeout and trigger levels, disables loopback, requests IRQ, and enables RX/error interrupts. IRQ handling clears latched status, reports break/frame/overrun events, drains RX FIFO, and transmits pending bytes on TX interrupts. Termios forces 8N1, rejects modem-style flags, computes the closest rate divider, toggles RX/error interrupts for CREAD, writes the divider, and updates timeout.

## State and Persistence Behavior

State is mostly static per-port `uart_port` data plus the global `uarts_registered` count. Hardware loopback is used as a quiescent state outside active use. PM suspend/resume delegates to `uart_suspend_port()` and `uart_resume_port()`; detailed register restoration is not locally cached.

## Dependencies and Integration Points

Dependencies include serial core, platform resources, OF matching (`nxp,lpc3220-hsuart`), LPC32xx misc loopback helper `lpc32xx_loopback_set()`, console core, NMI watchdog touch in console write, and MMIO accessors.

## Risks and Edge Cases

Probe registration is order-based rather than alias-based, so device order matters. Termios masks off `CLOCAL` and `CRTSCTS`; applications expecting modem control or hardware flow will not get it. Only framing errors, break, and overrun are represented; parity is not supported. `uarts_registered` is not decremented on remove, limiting reprobe scenarios.

## Test Signals

Exercise all three ports, loopback transitions on startup/shutdown, forced termios normalization to 8N1, baud divider accuracy, RX timeout/trigger interrupts, break and overrun handling, console output during oops, PM suspend/resume, and remove/reprobe behavior.
