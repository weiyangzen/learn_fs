# sources/distributed-fs/ceph-client/drivers/tty/serial/serial-tegra.c

## Purpose
High-speed UART platform driver for NVIDIA Tegra SoCs. It registers `ttyTHS*` ports, supports PIO and DMA TX/RX paths, SoC-specific FIFO and clock quirks, modem control, suspend/resume through serial core, and device-tree configuration.

## Important APIs, Types, And Functions
`struct tegra_uart_chip_data` captures SoC capabilities: FIFO full status, FIFO reset behavior, clock source divider support, FIFO enable status, max port count, DMA burst size, and baud tolerance. `struct tegra_uart_port` embeds `uart_port` and tracks clock/reset, register shadows, DMA channels/buffers/descriptors/cookies, current baud, RX/TX progress, modem interrupt enablement, and DT baud tolerance entries. `tegra_uart_ops` implements serial callbacks. Central functions include `tegra_uart_probe()`, `tegra_uart_parse_dt()`, `tegra_uart_startup()`, `tegra_uart_hw_init()`, `tegra_uart_isr()`, DMA completion handlers, `tegra_uart_set_termios()`, and `tegra_uart_hw_deinit()`.

## Control Flow
Module init finds a matching OF node to size `tegra_uart_driver.nr`, registers the UART driver, then registers the platform driver. Probe matches chip data, parses DT alias and DMA availability, maps MMIO, obtains clock/reset/IRQ, and calls `uart_add_one_port()`. Startup allocates DMA channels unless PIO was selected, initializes hardware, requests IRQ, and enables receive interrupts. ISR loops on IIR: modem changes update serial-core counters, TX interrupt drains PIO TX, RX status/timeout/EORD dispatches PIO or DMA receive termination/restart, and line errors are decoded before tty insertion. Shutdown deinitializes hardware, drains/frees DMA, disables clock, and frees IRQ.

## State And Persistence
All state is runtime-only. Register shadows (`fcr_shadow`, `mcr_shadow`, `lcr_shadow`, `ier_shadow`) are authoritative for writes. DMA buffer mappings persist for an open port and are freed on shutdown. Device tree controls line number, modem interrupt support, DMA mode, and optional baud adjustment ranges.

## Dependencies And Integration Points
Depends on serial core, tty, DMAengine, clk, reset controller, platform/OF APIs, MMIO accessors, and system sleep PM. DT compatibles include Tegra20, Tegra30, Tegra186, and Tegra194 HSUART variants.

## Risks
DMA and PIO interleaving is complex, especially residue handling, alignment fallback, and flow-control RTS suppression around RX termination. FIFO reset requires SoC-specific waits to avoid data loss. Baud programming must satisfy chip-data tolerance or returns `-EIO`. Shutdown waits for TX empty and may report unready slaves when CTS flow control blocks drain.

## Test Signals
Boot with each compatible, verify `serial` aliases map expected lines, run RX/TX in pure PIO and DMA modes, test unaligned TX FIFO fallback, suspend/resume active ports, change baud/parity/stop/flow control, inject RX line errors, monitor DMA residue correctness, and verify FIFO reset waits prevent lost bytes.
