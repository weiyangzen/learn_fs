# sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl011.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl011.c` is the full Linux serial-core driver for ARM PL011-family UARTs, including ARM, ST-Ericsson, NVIDIA, SBSA UART, ACPI SPCR/QDF2400 erratum handling, DMA, RS485, console, earlycon, polling, and PM support. It exposes up to fourteen `ttyAMA` ports. The source was read as a complete 3223-line file.

## Important APIs, Types, and Functions

`struct vendor_data` captures register offsets, FIFO thresholds, flag bit meanings, access width, oversampling, DMA threshold quirks, always-enabled/fixed-option SBSA behavior, and optional FIFO sizing. `struct uart_amba_port` wraps `uart_port` and stores vendor offsets, clock, interrupt mask, FIFO size, RS485 timers/state, console tracking, and optional DMA state. DMA support is split into `struct pl011_dmatx_data`, `struct pl011_dmarx_data`, and `struct pl011_dmabuf`.

Core data paths include `pl011_fifo_to_tty()`, `pl011_rx_chars()`, `pl011_tx_chars()`, `pl011_int()`, `pl011_dma_tx_refill()`, `pl011_dma_tx_callback()`, `pl011_dma_rx_trigger_dma()`, `pl011_dma_rx_irq()`, `pl011_dma_rx_callback()`, and `pl011_dma_rx_poll()`. Serial-core ops are `amba_pl011_pops` and `sbsa_uart_pops`. Probe/register paths are `pl011_probe()`, `pl011_setup_port()`, `pl011_register_port()`, `sbsa_uart_probe()`, `pl011_remove()`, and `sbsa_uart_remove()`.

## Control Flow

AMBA probe chooses a free line, allocates a port, gets the clock, selects vendor data from AMBA ID, handles `reg-io-width`, initializes RS485 hrtimers, maps resources, registers the shared UART driver if needed, and adds the port. SBSA probe follows a platform-driver path, requires or defaults a fixed baud rate, uses 32-bit access, and avoids control-register programming that firmware owns.

Startup runs `pl011_hwinit()` to select pinctrl default state, enable the clock, clear pending errors/RX status, seed interrupt masks, and run platform `init()`. It requests a shared IRQ, programs FIFO trigger levels, enables UART/RX/TX according to RS485 mode, snapshots modem inputs, starts DMA if channels and buffers are available, and enables RX/timeout interrupts. IRQ handling reads raw status masked by `uap->im`, applies the ST CTS workaround if needed, clears non-RX/TX status, drains RX via DMA or PIO, updates modem state, and services TX.

TX favors DMA when enough queued data exists; otherwise PIO sends an x_char and then FIFO data, stopping TX interrupts when the queue empties. RX DMA uses alternating coherent page buffers, residue checks, DMA pause/terminate on timeout interrupts, a completion callback for full buffers, and an optional polling timer that falls back to interrupt mode after inactivity. RS485 uses `trigger_start_tx` and `trigger_stop_tx` hrtimers to honor before/after-send delays, gate RTS polarity, and optionally disable RX during transmit.

Termios computes baud based on 8x/16x oversampling and optional clock-rate programming, updates status masks, hardware flow control bits, ST oversampling bits, integer/fractional divisors unless the vendor skips them, and writes LCRH after divisors. Shutdown masks interrupts, stops DMA, stops RS485 transmit, frees IRQ, disables UART/FIFOs/break where allowed, disables clocks and pinctrl, runs platform `exit()`, and flushes DMA buffers.

## State and Persistence Behavior

State is held in `amba_ports[]`, per-port interrupt mask `im`, DMA channel/buffer state, hrtimers, cached modem status, console `console_line_ended`, UART registers, and clock/pinctrl state. No disk persistence exists. Hardware register state is deliberately preserved for SBSA always-enabled ports and for console/earlycon handoff. PM calls serial-core suspend/resume, with console paths able to run through nbcon atomic/threaded writers at any time.

## Dependencies and Integration Points

The driver depends on AMBA, platform devices, ACPI, OF aliases, serial core, TTY flip buffers, DMAengine, clocks, pinctrl, earlycon, nbcon console APIs, sysrq, and optional AMBA platform data. It integrates with ACPI SPCR through SBSA and QDF2400 E44 early console matching, and with device tree through `arm,pl011`, `arm,sbsa-uart`, and serial aliases.

## Risks and Edge Cases

High-risk areas are DMA fallback and residue accounting, RX FIFO threshold behavior after startup, RS485 timer/state transitions under concurrent TX stop/start, vendor register-offset differences, ST split LCRH ordering and CTS workaround, NVIDIA clock programming and skipped divisors, SBSA fixed-options behavior, and QDF2400 E44 inverted/busy flag handling. `amba_ports[]` is shared by AMBA and SBSA paths; alias collisions are warned but enumeration can still be surprising.

## Test Signals

Strong signals include probe on ARM/ST/NVIDIA/SBSA variants, 8-bit and 32-bit register access, DMA TX/RX with fallback injection, RX timeout and poll-mode behavior, high-baud ST oversampling, RS485 before/after delay and RX-during-TX combinations, modem status interrupts, console and earlycon takeover including QDF2400 E44, suspend/resume with console active, OF alias conflicts, and fault injection around clock, IRQ, DMA channel, and UART registration failures.
