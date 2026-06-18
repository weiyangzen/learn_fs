# sources/distributed-fs/ceph-client/drivers/tty/serial/sifive.c

## Purpose

`sifive.c` is the serial-core driver for SiFive UART v0 hardware, which is not 8250-compatible and intentionally supports a small feature set: 8-bit characters, configurable stop bits, RX/TX FIFO watermarks, console, earlycon, console polling, clock-rate notification, and platform/OF probing. It registers `ttySIF` ports through a `sifive-serial` UART driver. The source was read as a complete 1150-line file.

## Important APIs, Types, and Functions

The register contract is defined by `SIFIVE_SERIAL_*` offsets and masks for `TXDATA`, `RXDATA`, `TXCTRL`, `RXCTRL`, interrupt enable/pending, and divisor registers. `struct sifive_serial_port` embeds `struct uart_port` and adds a device pointer, a shadow interrupt-enable byte `ier`, current `baud_rate`, clock handle, clock notifier, and console line-ended state.

Low-level helpers are `__ssp_early_readl()`, `__ssp_early_writel()`, `__ssp_readl()`, `__ssp_writel()`, `sifive_serial_is_txfifo_full()`, `__ssp_transmit_char()`, `__ssp_transmit_chars()`, RX/TX watermark enable/disable helpers, `__ssp_receive_char()`, `__ssp_receive_chars()`, `__ssp_update_div()`, `__ssp_update_baud_rate()`, `__ssp_set_stop_bits()`, and `__ssp_wait_for_xmitr()`. UART operations are in `sifive_serial_uops`; probe/remove/PM are `sifive_serial_probe()`, `sifive_serial_remove()`, `sifive_serial_suspend()`, and `sifive_serial_resume()`.

## Control Flow

Module init registers the UART driver, then the platform driver. Probe obtains IRQ, maps MMIO, enables the clock, reads the `serial` alias as the UART line, allocates `struct sifive_serial_port`, registers a clock notifier, programs the initial divisor for 115200 baud, enables TX and RX hardware with watermark levels, requests the IRQ, adds the port to the console lookup table, and calls `uart_add_one_port()`.

The IRQ handler locks the port, reads interrupt-pending bits, drains RX when the RX watermark is pending, transmits queued chars when the TX watermark is pending, then unlocks through `uart_unlock_and_check_sysrq()`. Startup only enables RX watermark interrupts; start/stop TX toggle the TX watermark bit in the shadowed `ier`. Termios rejects unsupported word lengths, parity checking, and break handling by coercing flags and logging once, sets stop bits and baud divisor, updates timeout, and toggles RX enable according to `CREAD`. Console and earlycon write directly by waiting for TX FIFO space and writing `TXDATA`; the normal console uses nbcon atomic/thread callbacks and temporarily disables hardware interrupts around console output.

## State and Persistence Behavior

Per-port state is allocated with devm and lives until platform remove. The hardware divisor tracks `ssp->baud_rate` and `port.uartclk`; `ier` shadows the hardware interrupt enable register so watermark toggles do not require read-modify-write state from MMIO. The clock notifier updates `port.uartclk` and divisor after clock rate changes. Console state uses `sifive_serial_console_ports[]` and `console_line_ended` to prepend a newline for atomic writes that interrupt an unfinished line. There is no persistent storage beyond live hardware and driver memory.

## Dependencies and Integration Points

The driver depends on serial core, tty flip buffers, console/nbcon, earlycon, OF aliases and compatibles (`sifive,uart0`, `sifive,fu540-c000-uart`), platform resources, IRQs, clocks, and clock notifiers. It uses `uart_port_tx_limited()`, `uart_insert_char()`, `uart_prepare_sysrq_char()`, `uart_set_options()`, `uart_suspend_port()`, and `uart_resume_port()` for UART-core integration.

## Risks and Edge Cases

The hardware lacks parity, break, flow control, and modem signals, so termios callers may think requested settings were accepted unless they inspect coerced flags and one-time logs. `sifive_serial_tx_empty()` always returns empty because the hardware lacks a shift-register empty signal, while the clock notifier approximates drain time with a worst-case delay after TX FIFO empty. The divisor mask definition references `SIFIVE_SERIAL_IP_DIV_SHIFT`, which is not defined in the file and would be a compile-time risk if the mask were used. Probe only checks `id > SIFIVE_SERIAL_MAX_PORTS` under console config, leaving an off-by-one concern because valid indexes are `0..MAX_PORTS-1`. Busy waits in console/poll paths can spin indefinitely if hardware never frees TX space.

## Test Signals

Validation should include OF probe with valid and missing aliases, IRQ-driven RX/TX, console and nbcon atomic/thread writes, earlycon output, clock-rate change notification while TX is active, termios coercion for unsupported parity/break/word sizes, `CREAD` enable/disable, suspend/resume, remove cleanup of IRQ and notifier, and stress around TX watermark interrupts and sysrq reception.
