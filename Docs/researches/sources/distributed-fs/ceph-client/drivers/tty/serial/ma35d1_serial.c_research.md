# sources/distributed-fs/ceph-client/drivers/tty/serial/ma35d1_serial.c

## Purpose

`ma35d1_serial.c` is the Nuvoton MA35D1 UART driver. It supports up to 17 UARTs, MMIO FIFO operation, modem/auto-flow control, RS-485 function selection constants, console support, platform PM callbacks, and OF-based probing.

## Important APIs, Types, and Functions

`struct uart_ma35d1_port` wraps `struct uart_port` with a clock, local `ier/lcr/mcr` fields, and console register caches. `ma35d1serial_ops` exposes serial-core operations. Key routines include `serial_in()`, `serial_out()`, `transmit_chars()`, `receive_chars()`, `ma35d1serial_interrupt()`, `ma35d1serial_set_mctrl()`, `ma35d1serial_set_termios()`, `ma35d1serial_startup()`, `ma35d1serial_probe()`, `ma35d1serial_suspend()`, and `ma35d1serial_resume()`.

## Control Flow

Probe requires a DT node and serial alias, selects a static port slot, maps MMIO, obtains/enables the UART clock, obtains the IRQ, initializes the port, and registers with serial core. Startup resets FIFOs, clears pending interrupts, requests the IRQ, configures FIFO thresholds, default 8-bit LCR, RX timeout, and RX/buffer/time-out interrupts. The interrupt handler checks receive, timeout, TX-empty, and buffer-error conditions, calls `receive_chars()` or `transmit_chars()`, and clears TX overflow. Termios builds LCR from character format, computes baud as `uartclk / (quot + 2)`, updates read/ignore masks, toggles auto RTS/CTS via `ma35d1serial_set_mctrl()`, and writes baud/LCR.

## State and Persistence Behavior

Static `ma35d1serial_ports[MA35_UART_NR]` persists per-line objects. Runtime state is split between serial-core fields, cached `mcr`, and hardware registers. Suspend caches BAUD/LCR/IER only for console line 0 before `uart_suspend_port()` and restores them before `uart_resume_port()` on resume.

## Dependencies and Integration Points

The file depends on OF aliases, platform resources, clocks, MMIO, serial core, tty flip buffers, console core, and `read_poll_timeout_atomic()` for console TX waits. Compatible string is `nuvoton,ma35d1-uart`.

## Risks and Edge Cases

Console setup independently `ioremap()`s from DT `reg`, which must remain coherent with normal probe mapping. Probe error cleanup calls `free_irq()` after `uart_add_one_port()` failure even though request_irq occurs later in startup. `remove()` disables the clock but does not unmap normal probe MMIO. Flow-control polarity is hardcoded through active-level bits and needs hardware validation.

## Test Signals

Probe all alias lines, console line 0 boot/resume, baud bounds at divider min/max, CRTSCTS auto-flow enable/disable, break/parity/frame/overrun RX paths, TX overflow clearing, IRQ request failure, clock failures, suspend/resume with active console, and module unload.
