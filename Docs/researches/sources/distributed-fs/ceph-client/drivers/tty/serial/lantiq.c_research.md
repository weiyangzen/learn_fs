# sources/distributed-fs/ceph-client/drivers/tty/serial/lantiq.c

## Purpose

`lantiq.c` is a serial-core driver for the Lantiq ASC UART and Intel LGM ASC-compatible UARTs. It handles MMIO programming, FIFO/baud setup, interrupt variants, console and earlycon support, and device-tree platform probing.

## Important APIs, Types, and Functions

Important types are `struct ltq_uart_port`, which wraps `struct uart_port` with clocks, IRQ numbers, a private lock, and SoC hooks, and `struct ltq_soc_data`, which abstracts legacy three-IRQ Lantiq versus common-IRQ Intel wiring. The `lqasc_pops` `uart_ops` exposes startup/shutdown, termios, TX/RX control, request/release/config/verify, and modem stubs. Key functions include `lqasc_rx_chars()`, `lqasc_start_tx()`, `lqasc_startup()`, `lqasc_set_termios()`, `fetch_irq_lantiq()`, `request_irq_lantiq()`, `fetch_irq_intel()`, `request_irq_intel()`, and `lqasc_probe()`.

## Control Flow

Probe obtains MMIO resources, SoC match data, IRQ topology, alias line, clocks, and registers a `uart_port` in the static `lqasc_port` array. Startup enables the ASC clock gate, sets the run-mode clock divider, programs FIFO control, enables core UART mode and error reporting, requests SoC-specific IRQs, and enables RX/error/TX interrupts. RX IRQs clear interrupt status, drain the FIFO, read error bits, clear parity/frame/overrun state, and insert flip chars. TX IRQs acknowledge and call `uart_port_tx()` while FIFO space is available. Termios rewrites character size, parity, stop bits, masks, baud divisor, and receiver enable.

## State and Persistence Behavior

State persists in `lqasc_port[MAXPORTS]`, per-port clocks, IRQ ids, and hardware registers. The driver tracks read/ignore masks in `uart_port`, but modem control is mostly fixed as asserted. No suspend/resume state is implemented here; state is reconstructed by serial-core startup and termios paths.

## Dependencies and Integration Points

Dependencies include `clk`, device tree matching, Linux serial core, console/earlycon, Lantiq platform helpers for older non-common-clock builds, and raw MMIO. Device-tree compatibles are `lantiq,asc` and `intel,lgm-asc`.

## Risks and Edge Cases

The alias fallback for legacy Lantiq relies on physical address matching. `lqasc_remove()` removes the port but does not clear `lqasc_port[line]`, which matters if devices can re-probe. `lqasc_set_termios()` updates control bits with set-only masks in places, so stale bits must be considered when changing formats. Separate IRQ request cleanup is explicit and must remain matched to topology.

## Test Signals

Boot console and earlycon output, both `lantiq,asc` and `intel,lgm-asc` IRQ modes, RX errors and overrun clearing, termios changes for CS7/CS8/parity/stop bits, baud-rate accuracy, missing aliases, duplicate line allocation, clock-gate enable/disable, and module unload/reload behavior.
